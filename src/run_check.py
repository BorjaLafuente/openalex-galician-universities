"""
Run a single SQL file against the database and print the full result.

Meant for ad-hoc checks and exploration (sql/checks/), whose results are
looked at but not saved. Indicator queries use run_queries.py instead.

Usage, from the project root:
    python src/run_check.py sql/checks/diamond_sources_udc.sql
"""

import sqlite3
import sys                 # gives access to the command-line arguments
from pathlib import Path

import pandas as pd

DB_FILE = Path("data/openalex.db")


def main():
    # sys.argv is the list of words typed after "python":
    #   ["src/run_check.py", "sql/checks/diamond_sources_udc.sql"]
    # Position 0 is the script itself; position 1 is the SQL file.
    if len(sys.argv) != 2:
        print("Usage: python src/run_check.py <path/to/query.sql>")
        sys.exit(1)  # stop with an error code

    query_file = Path(sys.argv[1])
    query = query_file.read_text(encoding="utf-8")

    conn = sqlite3.connect(DB_FILE)
    try:
        result = pd.read_sql(query, conn)
    finally:
        conn.close()

    print(f"=== {query_file} ({len(result)} rows)\n")
    # to_string() prints every row and column, without truncating
    print(result.to_string(index=False))


if __name__ == "__main__":
    main()