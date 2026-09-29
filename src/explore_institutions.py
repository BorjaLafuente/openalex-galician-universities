"""
Exploration: find the OpenAlex ID of each Galician university.

The IDs are needed later to filter each university's publications.
Results are stored in config.py.
"""

import requests

from config import API_KEY, BASE_URL


def search_institution(name):
    """Search institutions by name and return the list of matches."""
    params = {
        "search": name,
        # Ask only for the fields we need instead of the full record
        "select": "id,display_name,country_code,works_count",
        "api_key": API_KEY,
    }
    response = requests.get(f"{BASE_URL}/institutions", params=params, timeout=30)
    response.raise_for_status()  # stop with a clear error on 4xx/5xx responses
    return response.json()["results"]


universities = [
    "Universidade da Coruña",
    "Universidade de Santiago de Compostela",
    "Universidade de Vigo",
]

for name in universities:
    print(f"\n{name}")
    # Show the top 3 matches: text search may also return related
    # institutions (hospitals, foundations...), so we pick the right one by eye.
    for inst in search_institution(name)[:3]:
        print(f"  {inst['id']}  {inst['display_name']} "
              f"({inst['country_code']}) - {inst['works_count']} works")