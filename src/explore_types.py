"""
Exploration: publications by document type and year.

Hypothesis: the ups and downs in the yearly totals come from changes in the
mix of document types (preprints, datasets, conference papers...) rather than
from real changes in research output.

Finding: partly confirmed. Non-article types add noise (e.g. a one-off spike
of datasets in 2019), but articles also dip after the 2020-2021 peak.
Decision: keep articles, reviews and conference papers (see README).
"""

import pandas as pd
import requests

from config import API_KEY, BASE_URL, UNIVERSITIES, YEAR_FROM, YEAR_TO


def count_works_by_type(institution_id, year):
    """Return the number of works per document type for one institution and year."""
    params = {
        "filter": (
            f"authorships.institutions.lineage:{institution_id},"
            f"publication_year:{year}"
        ),
        "group_by": "type",
        "api_key": API_KEY,
    }
    response = requests.get(f"{BASE_URL}/works", params=params, timeout=30)
    response.raise_for_status()
    return response.json()["group_by"]


# group_by only accepts one field, so we loop over years to get type x year
rows = []
for acronym, inst_id in UNIVERSITIES.items():
    for year in range(YEAR_FROM, YEAR_TO + 1):  # range() excludes the end value
        for group in count_works_by_type(inst_id, year):
            rows.append({
                "university": acronym,
                "year": year,
                "type": group["key_display_name"],
                "works": group["count"],
            })

types = pd.DataFrame(rows)

# Table 1: UDC publications by type and year
udc = (
    types[types["university"] == "UDC"]
    .pivot(index="type", columns="year", values="works")
    .fillna(0)       # types missing in some years -> 0
    .astype(int)
)
udc["total"] = udc.sum(axis=1)
print("UDC: publications by type and year")
print(udc.sort_values("total", ascending=False))

# Table 2: articles only, by university
articles = (
    types[types["type"] == "article"]
    .pivot(index="year", columns="university", values="works")
)
print("\nArticles only")
print(articles)