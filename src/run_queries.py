"""
Run every indicator query in sql/ and save each result as a CSV in results/.

Queries are plain .sql files named with a number prefix (01_..., 02_...),
so they run in order and can also be opened in any SQL tool.

Run from the project root:  python src/run_queries.py
"""

import sqlite3
from pathlib import Path

import pandas as pd

DB_FILE = Path("data/openalex.db")
SQL_DIR = Path("sql")
RESULTS_DIR = Path("results")


def main():
    RESULTS_DIR.mkdir(exist_ok=True)

    # glob("[0-9]*.sql") finds the numbered query files (skipping schema.sql);
    # sorted() makes them run in order: 01, 02, 03...
    query_files = sorted(SQL_DIR.glob("[0-9]*.sql"))

    conn = sqlite3.connect(DB_FILE)
    try:
        for query_file in query_files:
            query = query_file.read_text(encoding="utf-8")

            # read_sql runs the query and returns the result as a DataFrame
            result = pd.read_sql(query, conn)

            # Save with the same name as the query: 01_x.sql -> 01_x.csv
            out_file = RESULTS_DIR / f"{query_file.stem}.csv"
            result.to_csv(out_file, index=False)

            print(f"\n=== {query_file.name} -> {out_file} ({len(result)} rows)")
            print(result.head(15).to_string(index=False))
    finally:
        conn.close()  # always close the connection, even after an error


if __name__ == "__main__":
    main()
