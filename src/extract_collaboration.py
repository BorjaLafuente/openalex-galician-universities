"""
Step 1b of the pipeline - Extract collaboration: who do the universities
publish with?

Instead of downloading the authors of every work, OpenAlex counts the works
server-side with group_by, for each university and year (articles and
reviews only, as in the main indicators):

  - by co-author country      -> data/clean/collab_countries.csv
  - by co-author institution  -> data/clean/collab_institutions.csv
    (two counts per institution: by lineage and by direct affiliation)

Then it downloads the type, country and coordinates of every institution
found, which the dashboard needs to filter and map them:

  - institution details       -> data/clean/institutions.csv

Notes on the counts (see docs/findings.md):
  - Full counting: a work with authors from France and Italy counts once
    for each country.
  - The university's own country (ES) and the university itself are kept:
    their count equals the total number of works, a useful denominator.
    They are filtered out in SQL when only partners are needed.
  - Institutions are counted in two ways:
      n_works         grouped by lineage: a work with a CSIC institute also
                      counts for CSIC as a whole, and for any parent body
                      above it (e.g. a ministry).
      n_works_direct  direct affiliation only: the institution the authors
                      actually wrote on the paper.
    Parent bodies that only appear through lineage (ministries, regional
    governments, umbrella networks) have n_works_direct = 0 or close to it,
    which lets them be told apart from real research partners.

Run from the project root:  python src/extract_collaboration.py
"""

from datetime import date
from pathlib import Path

import pandas as pd

from config import API_KEY, BASE_URL, UNIVERSITIES, YEAR_FROM, YEAR_TO
from extract import get_json
from transform import strip_prefix

CLEAN_DIR = Path("data/clean")
COUNTRIES_FILE = CLEAN_DIR / "collab_countries.csv"
INSTITUTIONS_FILE = CLEAN_DIR / "collab_institutions.csv"
INSTITUTION_INFO_FILE = CLEAN_DIR / "institutions.csv"

DOC_TYPES = ["article", "review"]

# OpenAlex returns at most 200 groups per page. If a page is full, the rest
# come in further pages, requested with a cursor as in extract.py.
GROUPS_PER_PAGE = 200
MAX_PAGES = 200  # safety limit, so a paging problem can never loop forever

# Maximum number of IDs combined with | (OR) in a single filter
IDS_PER_REQUEST = 50


def get_groups(institution_id, year, field):
    """Count one year of works of one university, grouped by `field`.

    Returns a list of groups like
    {"key": "https://openalex.org/countries/US", "key_display_name":
    "United States", "count": 119}.
    """
    params = {
        "filter": (
            f"authorships.institutions.lineage:{institution_id},"
            f"publication_year:{year},"
            f"type:{'|'.join(DOC_TYPES)}"
        ),
        "group_by": field,
        "per_page": GROUPS_PER_PAGE,
        "cursor": "*",
        "api_key": API_KEY,
    }

    groups = []
    for _ in range(MAX_PAGES):
        data = get_json(f"{BASE_URL}/works", params)
        groups.extend(data["group_by"])

        next_cursor = data["meta"].get("next_cursor")
        if not next_cursor or not data["group_by"]:
            break
        params["cursor"] = next_cursor

    return groups


def extract_countries():
    """Works per university, year and co-author country."""
    rows = []
    for acronym, inst_id in UNIVERSITIES.items():
        for year in range(YEAR_FROM, YEAR_TO + 1):
            groups = get_groups(inst_id, year, "authorships.countries")
            for g in groups:
                rows.append({
                    "university": acronym,
                    "year": year,
                    # "https://openalex.org/countries/US" -> "US" (ISO code)
                    "country_code": strip_prefix(g["key"], "https://openalex.org/countries/"),
                    "country_name": g["key_display_name"],
                    "n_works": g["count"],
                })
            print(f"  {acronym} {year}: {len(groups)} countries")
    return pd.DataFrame(rows)


def extract_institutions():
    """Works per university, year and co-author institution, counted by
    lineage and by direct affiliation."""
    rows = []
    for acronym, inst_id in UNIVERSITIES.items():
        for year in range(YEAR_FROM, YEAR_TO + 1):
            lineage = get_groups(inst_id, year, "authorships.institutions.lineage")
            direct = get_groups(inst_id, year, "authorships.institutions.id")

            # Direct counts as a dictionary {institution ID: count}, to look
            # them up quickly while going through the lineage groups
            direct_counts = {
                strip_prefix(g["key"], "https://openalex.org/"): g["count"]
                for g in direct
            }

            # Every institution with a direct affiliation is also in its own
            # lineage, so the lineage groups contain all institutions.
            # Institutions reached only through lineage get a direct count of 0.
            for g in lineage:
                institution_id = strip_prefix(g["key"], "https://openalex.org/")
                rows.append({
                    "university": acronym,
                    "year": year,
                    "institution_id": institution_id,
                    "n_works": g["count"],
                    "n_works_direct": direct_counts.get(institution_id, 0),
                })

            print(f"  {acronym} {year}: {len(lineage)} institutions by lineage, "
                  f"{len(direct)} by direct affiliation")
    return pd.DataFrame(rows)


def extract_institution_info(institution_ids):
    """Download name, type, country and coordinates of each institution."""
    fields = ["id", "display_name", "type", "country_code", "geo"]
    rows = []

    # Ask for the institutions in batches: filter=openalex_id:I1|I2|...|I50
    for start in range(0, len(institution_ids), IDS_PER_REQUEST):
        batch = institution_ids[start:start + IDS_PER_REQUEST]
        params = {
            "filter": f"openalex_id:{'|'.join(batch)}",
            "select": ",".join(fields),
            "per_page": IDS_PER_REQUEST,
            "api_key": API_KEY,
        }
        data = get_json(f"{BASE_URL}/institutions", params)

        for inst in data["results"]:
            geo = inst.get("geo") or {}  # some institutions have no geo data
            rows.append({
                "institution_id": strip_prefix(inst["id"], "https://openalex.org/"),
                "name": inst["display_name"],
                "type": inst.get("type"),
                "country_code": inst.get("country_code"),
                "city": geo.get("city"),
                "latitude": geo.get("latitude"),
                "longitude": geo.get("longitude"),
            })

        print(f"  institution details: {len(rows)} of {len(institution_ids)}", end="\r")

    print()
    return pd.DataFrame(rows)


def main():
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()  # extraction date, e.g. "2026-10-13"

    # Each file is skipped if it already exists, so the script can be
    # resumed, and a single file can be refreshed by deleting only that file.
    if COUNTRIES_FILE.exists():
        print(f"{COUNTRIES_FILE} already exists, skipping")
    else:
        print("Downloading counts by country...")
        countries = extract_countries()
        # OpenAlex changes every day: keep the date the counts refer to
        countries["extracted_on"] = today
        countries.to_csv(COUNTRIES_FILE, index=False)
        print(f"Saved {len(countries)} rows to {COUNTRIES_FILE}")

    if INSTITUTIONS_FILE.exists():
        print(f"{INSTITUTIONS_FILE} already exists, skipping")
        institutions = pd.read_csv(INSTITUTIONS_FILE)
    else:
        print("Downloading counts by institution...")
        institutions = extract_institutions()
        institutions["extracted_on"] = today
        institutions.to_csv(INSTITUTIONS_FILE, index=False)
        print(f"Saved {len(institutions)} rows to {INSTITUTIONS_FILE}")

    if INSTITUTION_INFO_FILE.exists():
        print(f"{INSTITUTION_INFO_FILE} already exists, skipping")
    else:
        ids = sorted(institutions["institution_id"].unique())
        print(f"Downloading details of {len(ids)} institutions...")
        info = extract_institution_info(ids)
        info.to_csv(INSTITUTION_INFO_FILE, index=False)
        print(f"Saved {len(info)} rows to {INSTITUTION_INFO_FILE}")


if __name__ == "__main__":
    main()
