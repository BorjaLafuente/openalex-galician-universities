-- Database schema for the clean OpenAlex data.
-- Column meanings are documented in docs/data_dictionary.md.

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
