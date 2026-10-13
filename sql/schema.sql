-- Database schema for the clean OpenAlex data.
-- Column meanings are documented in docs/data_dictionary.md.

-- Tables that reference others are dropped first
DROP TABLE IF EXISTS collab_institutions;
DROP TABLE IF EXISTS collab_countries;
DROP TABLE IF EXISTS institutions;
DROP TABLE IF EXISTS work_universities;
DROP TABLE IF EXISTS works;

-- One row per unique publication
CREATE TABLE works (
    work_id          TEXT PRIMARY KEY,   -- unique: no duplicate works allowed
    doi              TEXT,
    title            TEXT,
    year             INTEGER NOT NULL,
    type             TEXT    NOT NULL,
    language         TEXT,
    is_oa            INTEGER,            -- SQLite has no boolean type: 1 = true, 0 = false
    oa_status        TEXT,
    source_id        TEXT,
    source_name      TEXT,
    source_type      TEXT,
    publisher        TEXT,
    issn_l           TEXT,
    issns            TEXT,
    domain           TEXT,
    field            TEXT,
    subfield         TEXT,
    cited_by_count   INTEGER,
    fwci             REAL,
    is_top10         INTEGER,
    is_top1          INTEGER,
    n_countries      INTEGER,
    n_institutions   INTEGER,
    is_international INTEGER
);

-- One row per (publication, university) pair
CREATE TABLE work_universities (
    work_id    TEXT NOT NULL REFERENCES works (work_id),  -- foreign key
    university TEXT NOT NULL,
    PRIMARY KEY (work_id, university)   -- each pair can appear only once
);

-- Index to speed up filtering and grouping by university
CREATE INDEX idx_work_universities_university ON work_universities (university);


-- ---------------------------------------------------------------------------
-- Collaboration tables, written by extract_collaboration.py.
-- They hold counts already aggregated by OpenAlex (group_by), not individual
-- works: articles and reviews per university, year and co-author.
-- ---------------------------------------------------------------------------

-- One row per institution found among the co-authors
CREATE TABLE institutions (
    institution_id TEXT PRIMARY KEY,
    name           TEXT NOT NULL,
    type           TEXT,      -- education, healthcare, government, company...
    country_code   TEXT,      -- ISO 3166-1 alpha-2, e.g. ES, US
    city           TEXT,
    latitude       REAL,
    longitude      REAL
);

-- Works per university, year and co-author country (full counting).
-- The university's own country (ES) is included: its count is the total.
CREATE TABLE collab_countries (
    university   TEXT    NOT NULL,
    year         INTEGER NOT NULL,
    country_code TEXT    NOT NULL,
    country_name TEXT,
    n_works      INTEGER NOT NULL,
    extracted_on TEXT    NOT NULL,   -- date of the OpenAlex counts (YYYY-MM-DD)
    PRIMARY KEY (university, year, country_code)
);

-- Works per university, year and co-author institution (full counting).
-- The university itself is included: its n_works is the total.
CREATE TABLE collab_institutions (
    university     TEXT    NOT NULL,
    year           INTEGER NOT NULL,
    institution_id TEXT    NOT NULL REFERENCES institutions (institution_id),
    n_works        INTEGER NOT NULL,   -- grouped by lineage (includes child institutions)
    n_works_direct INTEGER NOT NULL,   -- direct affiliation only; 0 = reached only via lineage
    extracted_on   TEXT    NOT NULL,
    PRIMARY KEY (university, year, institution_id)
);

CREATE INDEX idx_collab_institutions_institution ON collab_institutions (institution_id);
