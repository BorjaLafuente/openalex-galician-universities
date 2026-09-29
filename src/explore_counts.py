"""
Exploration: number of publications per year for each university.

group_by makes OpenAlex do the counting server-side: one request per
university, without downloading any publications.
"""

import pandas as pd
import requests

from config import API_KEY, BASE_URL, UNIVERSITIES, YEAR_FROM, YEAR_TO


def count_works_by_year(institution_id):
    """Return the number of works per publication year for one institution."""
    params = {
        # authorships.institutions.lineage matches works with at least one
        # author affiliated with the institution or any of its child
        # institutions (institutes, research centres...).
        "filter": (
            f"authorships.institutions.lineage:{institution_id},"
            f"publication_year:{YEAR_FROM}-{YEAR_TO}"
        ),
        "group_by": "publication_year",
        "api_key": API_KEY,
    }
    response = requests.get(f"{BASE_URL}/works", params=params, timeout=30)
    response.raise_for_status()
    # e.g. [{"key": "2015", "key_display_name": "2015", "count": 1313}, ...]
    return response.json()["group_by"]


# One row per university and year (long format)
rows = []
for acronym, inst_id in UNIVERSITIES.items():
    for group in count_works_by_year(inst_id):
        rows.append({
            "university": acronym,
            "year": int(group["key"]),  # the API returns the year as text
            "works": group["count"],
        })

counts = pd.DataFrame(rows)

# Wide format: one row per year, one column per university
table = counts.pivot(index="year", columns="university", values="works").sort_index()

print(table)
print(f"\nTotal {YEAR_FROM}-{YEAR_TO}:")
print(table.sum())