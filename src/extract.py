"""
Step 1 of the pipeline - Extract: download publications from the OpenAlex API.

For each university, downloads the articles, reviews and conference papers of
the analysis period and stores them raw (exactly as returned by the API) in
data/raw/<ACRONYM>.jsonl, one JSON record per line.
"""

import json
import time
from pathlib import Path

import requests

from config import API_KEY, BASE_URL, UNIVERSITIES, YEAR_FROM, YEAR_TO

RAW_DIR = Path("data/raw")

# Document types included in the analysis (see README, "Methodology")
DOC_TYPES = ["article", "review", "conference-paper"]

# Fields to download. authorships is left out on purpose: papers from large
# physics collaborations list thousands of authors and would inflate the
# download. countries_distinct_count is enough to flag international
# collaboration.
FIELDS = [
    "id", "doi", "title", "publication_year", "type", "language",
    "open_access", "primary_location", "primary_topic",
    "cited_by_count", "fwci", "citation_normalized_percentile",
    "countries_distinct_count", "institutions_distinct_count",
]


def get_json(url, params, max_retries=5):
    """GET request with retries on temporary API errors."""
    for attempt in range(1, max_retries + 1):
        response = requests.get(url, params=params, timeout=60)

        # 429 (too many requests) and 5xx (server errors) are usually
        # temporary: wait and retry, doubling the wait each time
        # (exponential backoff: 2, 4, 8, 16... seconds).
        if response.status_code in (429, 500, 502, 503, 504):
            wait = 2 ** attempt
            print(f"\n    Error {response.status_code}; retry {attempt} in {wait} s")
            time.sleep(wait)
            continue

        # Any other error (400 bad query, 401 bad key...) is on our side: stop.
        response.raise_for_status()
        return response.json()

    raise RuntimeError(f"The API did not respond after {max_retries} attempts")


def download_works(acronym, institution_id):
    """Download all works of one university into a .jsonl file."""
    out_file = RAW_DIR / f"{acronym}.jsonl"

    # Skip universities already downloaded, so an interrupted run can be
    # resumed without starting over.
    if out_file.exists():
        print(f"{acronym}: already downloaded ({out_file}), skipping")
        return

    params = {
        # In OpenAlex filters, | means OR: type is article OR review OR ...
        "filter": (
            f"authorships.institutions.lineage:{institution_id},"
            f"publication_year:{YEAR_FROM}-{YEAR_TO},"
            f"type:{'|'.join(DOC_TYPES)}"
        ),
        "select": ",".join(FIELDS),
        "per_page": 100,  # maximum allowed by the API
        # Cursor paging: the first request uses cursor="*" and each response
        # returns the cursor for the next page. An empty cursor means we are done.
        "cursor": "*",
        "api_key": API_KEY,
    }

    # Write to a temporary file and rename it only when complete, so an
    # interrupted download never leaves a partial .jsonl behind.
    tmp_file = out_file.with_suffix(".tmp")
    n_saved = 0

    with open(tmp_file, "w", encoding="utf-8") as f:
        while True:
            data = get_json(f"{BASE_URL}/works", params)

            if n_saved == 0:
                print(f"{acronym}: {data['meta']['count']} works to download")

            for work in data["results"]:
                # ensure_ascii=False keeps accents and other characters as is
                f.write(json.dumps(work, ensure_ascii=False) + "\n")
            n_saved += len(data["results"])

            # end="\r" rewrites the same line, so the counter updates in place
            print(f"  {acronym}: {n_saved} downloaded", end="\r")

            next_cursor = data["meta"].get("next_cursor")
            if not next_cursor or not data["results"]:
                break
            params["cursor"] = next_cursor

    tmp_file.rename(out_file)
    print(f"\n{acronym}: {n_saved} works saved to {out_file}")


# Runs only when the file is executed directly (python src/extract.py),
# not when another script imports its functions.
if __name__ == "__main__":
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for acronym, inst_id in UNIVERSITIES.items():
        download_works(acronym, inst_id)