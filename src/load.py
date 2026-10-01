"""
Step 3 of the pipeline - Load: store the clean tables in a SQLite database.

Creates data/openalex.db from sql/schema.sql and loads the two tables written
by transform.py. SQLite keeps the whole database in a single file and comes
built into Python, so there is no server to install.

Run from the project root:  python src/load.py
"""

import sqlite3             # SQLite driver, part of the standard library
from pathlib import Path

import pandas as pd

CLEAN_DIR = Path("data/clean")
DB_FILE = Path("data/openalex.db")
SCHEMA_FILE = Path("sql/schema.sql")


def main():
    # 1. Read the clean tables produced by transform.py
    works = pd.read_csv(CLEAN_DIR / "works.csv")
    work_universities = pd.read_csv(CLEAN_DIR / "work_universities.csv")

    # SQLite has no boolean type: store True/False as 1/0. "Int64" keeps
    # missing values as NULL instead of turning them into decimals.
    bool_cols = ["is_oa", "is_top10", "is_top1", "is_international"]
    works[bool_cols] = works[bool_cols].astype("boolean").astype("Int64")

    # 2. Open a connection to the database. connect() creates the file if it
    #    does not exist yet.
    conn = sqlite3.connect(DB_FILE)

    # try/finally: the "finally" block always runs, even if something inside
    # "try" fails, so the connection is always closed.
    try:
        # 3. Create the tables (dropping them first if they already exist),
        #    so the script can be re-run from scratch at any time.
        conn.executescript(SCHEMA_FILE.read_text(encoding="utf-8"))

        # 4. Insert the rows into the tables defined by the schema.
        #    if_exists="append" adds rows to the existing (empty) tables
        #    instead of letting pandas create its own, untyped ones.
        works.to_sql("works", conn, if_exists="append", index=False)
        work_universities.to_sql("work_universities", conn, if_exists="append", index=False)
        conn.commit()  # make the changes permanent

        # 5. Quick check: count the rows now in the database
        for table in ["works", "work_universities"]:
            n = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"{table}: {n} rows")
    finally:
        conn.close()

    print(f"\nDatabase saved to {DB_FILE}")


if __name__ == "__main__":
    main()
