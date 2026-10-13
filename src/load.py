"""
Step 3 of the pipeline - Load: store the clean tables in a SQLite database.

Creates data/openalex.db from sql/schema.sql and loads the tables written by
transform.py (works) and extract_collaboration.py (collaboration). SQLite
keeps the whole database in a single file and comes built into Python, so
there is no server to install.

Run from the project root:  python src/load.py
"""

import sqlite3             # SQLite driver, part of the standard library
from pathlib import Path

import pandas as pd

CLEAN_DIR = Path("data/clean")
DB_FILE = Path("data/openalex.db")
SCHEMA_FILE = Path("sql/schema.sql")

# Table name in the database -> CSV file in data/clean. Tables are loaded in
# this order, so a table always comes after the tables it references.
TABLES = {
    "works": "works.csv",
    "work_universities": "work_universities.csv",
    "institutions": "institutions.csv",
    "collab_countries": "collab_countries.csv",
    "collab_institutions": "collab_institutions.csv",
}


def main():
    # 1. Read the clean tables: {table name: DataFrame}
    data = {}
    for table, csv_file in TABLES.items():
        if table.startswith("collab") or table == "institutions":
            # By default pandas reads the text "NA" as a missing value, but
            # here "NA" is the country code of Namibia. Only empty cells
            # count as missing in these tables.
            data[table] = pd.read_csv(CLEAN_DIR / csv_file,
                                      keep_default_na=False, na_values=[""])
        else:
            data[table] = pd.read_csv(CLEAN_DIR / csv_file)

    # SQLite has no boolean type: store True/False as 1/0. "Int64" keeps
    # missing values as NULL instead of turning them into decimals.
    bool_cols = ["is_oa", "is_top10", "is_top1", "is_international"]
    data["works"][bool_cols] = data["works"][bool_cols].astype("boolean").astype("Int64")

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
        for table, df in data.items():
            df.to_sql(table, conn, if_exists="append", index=False)
        conn.commit()  # make the changes permanent

        # 5. Quick check: count the rows now in the database
        for table in TABLES:
            n = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"{table}: {n} rows")
    finally:
        conn.close()

    print(f"\nDatabase saved to {DB_FILE}")


if __name__ == "__main__":
    main()
