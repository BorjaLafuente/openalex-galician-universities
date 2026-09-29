"""
Step 2 of the pipeline - Transform: clean the raw OpenAlex records.

Reads data/raw/<ACRONYM>.jsonl, flattens the nested JSON fields and writes
two tables to data/clean/ (see docs/data_dictionary.md):
  - works.csv:              one row per unique publication
  - work_universities.csv:  one row per (publication, university) pair

Run from the project root:  python src/transform.py
"""

# --- Imports -----------------------------------------------------------------
# Standard library first, then third-party packages, then our own modules.

import html                # decode HTML entities in titles (&amp; -> &)
import json                # parse each line of the .jsonl files
from pathlib import Path   # build file paths that work on any OS

import pandas as pd

from config import UNIVERSITIES

# --- Settings ----------------------------------------------------------------

RAW_DIR = Path("data/raw")      # input: raw records written by extract.py
CLEAN_DIR = Path("data/clean")  # output: clean tables


# --- Helper functions --------------------------------------------------------

def get_nested(record, *keys):
    """Safely read a nested value.

    get_nested(work, "primary_location", "source", "display_name") returns
    work["primary_location"]["source"]["display_name"], or None if any level
    is missing or null (instead of raising an error).

    *keys collects any number of arguments into a tuple, so the function
    works for paths of any depth.
    """
    value = record
    for key in keys:
        # If the current level is not a dictionary (e.g. it is None because
        # the field was null in the JSON), we cannot go any deeper.
        if not isinstance(value, dict):
            return None
        # .get() returns None when the key does not exist, whereas
        # value[key] would raise a KeyError.
        value = value.get(key)
    return value


def strip_prefix(value, prefix):
    """Remove a URL prefix from a string, keeping None as None.

    Example: "https://openalex.org/W123" -> "W123"
    """
    if value is None:
        return None
    return value.removeprefix(prefix)


# --- Flattening --------------------------------------------------------------

def flatten_work(work):
    """Turn one nested OpenAlex record into a flat dictionary (one table row).

    Each key of the returned dictionary becomes a column of the works table.
    The mapping from OpenAlex fields to columns is documented in
    docs/data_dictionary.md.
    """
    # Values used more than once, or that need extra processing, are read
    # into variables first to keep the dictionary below readable.
    title = work.get("title")
    n_countries = work.get("countries_distinct_count")
    source = get_nested(work, "primary_location", "source")  # journal/conference
    issns = get_nested(source, "issn")  # list of all ISSNs, or None

    return {
        # --- Identifiers ---
        # work["id"] (not .get) because every record has an ID: if it were
        # missing, something would be seriously wrong and an error is welcome.
        "work_id": strip_prefix(work["id"], "https://openalex.org/"),
        "doi": strip_prefix(work.get("doi"), "https://doi.org/"),

        # --- Basic metadata ---
        # Titles may contain HTML entities such as &amp; -> decode them
        "title": html.unescape(title) if title else None,
        "year": work.get("publication_year"),
        "type": work.get("type"),
        "language": work.get("language"),

        # --- Open access ---
        "is_oa": get_nested(work, "open_access", "is_oa"),
        "oa_status": get_nested(work, "open_access", "oa_status"),

        # --- Source (journal or conference) ---
        "source_id": strip_prefix(get_nested(source, "id"), "https://openalex.org/"),
        "source_name": get_nested(source, "display_name"),
        "source_type": get_nested(source, "type"),
        "publisher": get_nested(source, "host_organization_name"),
        # ISSN-L: one linking ISSN per journal, the best key to join external
        # lists (JCR, SJR...). issns: all ISSNs (print and electronic are not
        # labelled in OpenAlex), joined into one text value with ";".
        "issn_l": get_nested(source, "issn_l"),
        "issns": ";".join(issns) if issns else None,

        # --- Subject classification (three levels, from broad to narrow) ---
        "domain": get_nested(work, "primary_topic", "domain", "display_name"),
        "field": get_nested(work, "primary_topic", "field", "display_name"),
        "subfield": get_nested(work, "primary_topic", "subfield", "display_name"),

        # --- Citation impact ---
        "cited_by_count": work.get("cited_by_count"),
        "fwci": work.get("fwci"),  # Field-Weighted Citation Impact
        "is_top10": get_nested(work, "citation_normalized_percentile", "is_in_top_10_percent"),
        "is_top1": get_nested(work, "citation_normalized_percentile", "is_in_top_1_percent"),

        # --- Collaboration ---
        "n_countries": n_countries,
        "n_institutions": work.get("institutions_distinct_count"),
        # Conditional expression: "A if condition else B" (like ifelse() in R).
        # International = more than one country among the affiliations.
        "is_international": n_countries > 1 if n_countries is not None else None,
    }


# --- Main process ------------------------------------------------------------

def main():
    # works_by_id: a dictionary keyed by work_id. It keeps each publication
    # only once: if the same work appears in two universities' files, the
    # second one simply overwrites the first (the records are identical).
    works_by_id = {}

    # memberships: one entry per (work, university) pair. Here duplicates are
    # the point: a work shared by UDC and USC gets one entry for each.
    memberships = []

    # 1. Read and flatten the raw files, one university at a time
    for acronym in UNIVERSITIES:  # looping over a dict gives its keys
        raw_file = RAW_DIR / f"{acronym}.jsonl"
        n_read = 0
        with open(raw_file, encoding="utf-8") as f:
            # Read the file line by line instead of loading it all into
            # memory: each line is one complete JSON record.
            for line in f:
                row = flatten_work(json.loads(line))
                works_by_id[row["work_id"]] = row
                memberships.append({"work_id": row["work_id"], "university": acronym})
                n_read += 1
        print(f"{acronym}: {n_read} records read")

    # 2. Build the two tables
    # .values() gives the rows of the dictionary (without the keys)
    works = pd.DataFrame(list(works_by_id.values()))
    # drop_duplicates() is a safety net: the API should never return the same
    # work twice for one university, but if it did, we keep a single link.
    work_universities = pd.DataFrame(memberships).drop_duplicates()

    # 3. Set column types
    # Nullable types keep missing values as missing (<NA>). With the default
    # types, pandas would turn an integer column with gaps into decimals
    # (3 -> 3.0) and a boolean column with gaps into generic objects.
    bool_cols = ["is_oa", "is_top10", "is_top1", "is_international"]
    int_cols = ["year", "cited_by_count", "n_countries", "n_institutions"]
    works[bool_cols] = works[bool_cols].astype("boolean")
    works[int_cols] = works[int_cols].astype("Int64")  # capital I = nullable

    # 4. Save the tables
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    # index=False: do not write pandas' row numbers as an extra column
    works.to_csv(CLEAN_DIR / "works.csv", index=False)
    work_universities.to_csv(CLEAN_DIR / "work_universities.csv", index=False)

    # 5. Print a short data quality summary
    n_links = len(work_universities)
    print(f"\nUnique works: {len(works)}")
    print(f"Work-university links: {n_links} "
          f"({n_links - len(works)} extra links from shared publications)")

    # Count missing values per column (like colSums(is.na(df)) in R) and
    # show only the columns that have any.
    print("\nMissing values per column:")
    missing = works.isna().sum()
    print(missing[missing > 0].to_string())

    print(f"\nSaved to {CLEAN_DIR}/")


# Run main() only when the file is executed directly, not when imported
if __name__ == "__main__":
    main()
