"""
Shared project settings.

Other scripts import them with:  from config import API_KEY, ...
"""

import os

from dotenv import load_dotenv

# API key, read from the .env file (which is excluded by .gitignore)
load_dotenv()
API_KEY = os.getenv("OPENALEX_API_KEY")

BASE_URL = "https://api.openalex.org"

# Universities to analyse: acronym -> OpenAlex institution ID
UNIVERSITIES = {
    "UDC": "I11019714",     # Universidade da Coruña
    "USC": "I200284239",    # Universidade de Santiago de Compostela
    "UVIGO": "I6289922",    # Universidade de Vigo
}

# Analysis period
YEAR_FROM = 2015
YEAR_TO = 2025