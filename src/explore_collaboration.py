"""
Exploration: what does OpenAlex return when grouping works by co-author
country or co-author institution?

Before writing the real extraction script, check with a single university
and year:
  - what the keys look like (codes, full URLs...),
  - how many groups come back and whether paging is needed,
  - whether the university's own country and institution appear in the list.

Run from the project root:  python src/explore_collaboration.py
"""

from config import API_KEY, BASE_URL, UNIVERSITIES
from extract import get_json  # reuse the function with retries

ACRONYM = "UDC"
YEAR = 2024


def explore(group_by_field):
    """Group one year of UDC articles and reviews by the given field."""
    params = {
        # Same filter as the main extraction, but for one year and only
        # articles and reviews (the core of the analysis)
        "filter": (
            f"authorships.institutions.lineage:{UNIVERSITIES[ACRONYM]},"
            f"publication_year:{YEAR},"
            f"type:article|review"
        ),
        "group_by": group_by_field,
        "api_key": API_KEY,
    }
    data = get_json(f"{BASE_URL}/works", params)

    groups = data["group_by"]
    print(f"\n=== group_by={group_by_field}")
    print(f"Works matching the filter: {data['meta']['count']}")
    print(f"Groups in total (meta):    {data['meta'].get('groups_count')}")
    print(f"Groups in this response:   {len(groups)}")
    print("First 10 groups:")
    for g in groups[:10]:
        print(f"  {g['key']:<45} {g['key_display_name']:<45} {g['count']}")


explore("authorships.countries")
explore("authorships.institutions.lineage")
