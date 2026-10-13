# Data dictionary

The database (`data/openalex.db`) has two groups of tables.

**Publications** (written by `transform.py`):

- **`works`**: one row per unique publication.
- **`work_universities`**: one row per (publication, university) pair. A paper co-authored by UDC and USC appears once in `works` and twice here.

This avoids duplicating shared publications and models the many-to-many relationship between works and universities.

**Collaboration** (written by `extract_collaboration.py`):

- **`collab_countries`**: number of works per university, year and co-author country.
- **`collab_institutions`**: number of works per university, year and co-author institution.
- **`institutions`**: one row per institution found among the co-authors, with its type, country and location.

The collaboration tables hold counts already aggregated by OpenAlex (`group_by`), not individual works, so they cannot be joined to `works`. They cover **articles and reviews only**.

## `works`

| Column | Type | Source field in OpenAlex | Description |
|---|---|---|---|
| `work_id` | text | `id` (URL prefix removed) | OpenAlex work ID, e.g. `W2798336535`. Primary key. |
| `doi` | text | `doi` (`https://doi.org/` removed) | DOI, if any. |
| `title` | text | `title` | Title of the publication. |
| `year` | integer | `publication_year` | Publication year. |
| `type` | text | `type` | Document type: `article`, `review` or `conference-paper`. |
| `language` | text | `language` | Language code (ISO 639-1), e.g. `en`, `es`. |
| `is_oa` | boolean | `open_access.is_oa` | Whether a free-to-read version exists. |
| `oa_status` | text | `open_access.oa_status` | Open access route: `gold`, `diamond`, `hybrid`, `bronze`, `green` or `closed`. |
| `source_id` | text | `primary_location.source.id` (URL prefix removed) | OpenAlex source (journal/conference) ID, e.g. `S205231332`. |
| `source_name` | text | `primary_location.source.display_name` | Journal or conference where the work was published. |
| `source_type` | text | `primary_location.source.type` | Source type, e.g. `journal`, `conference`, `repository`. |
| `publisher` | text | `primary_location.source.host_organization_name` | Publisher of the source. |
| `issn_l` | text | `primary_location.source.issn_l` | Linking ISSN (ISSN-L): a single ISSN grouping the print and electronic versions of a journal. Best key to join external journal lists (JCR, SJR...). |
| `issns` | text | `primary_location.source.issn` | All ISSNs of the source, separated by `;`. OpenAlex does not label which one is print and which one electronic. |
| `domain` | text | `primary_topic.domain.display_name` | Broadest subject level (4 domains). |
| `field` | text | `primary_topic.field.display_name` | Subject field (26 fields). |
| `subfield` | text | `primary_topic.subfield.display_name` | Subject subfield (~250 subfields). |
| `cited_by_count` | integer | `cited_by_count` | Total citations received. |
| `fwci` | float | `fwci` | Field-Weighted Citation Impact: citations relative to the world average for works of the same field, year and type (1 = world average). |
| `is_top10` | boolean | `citation_normalized_percentile.is_in_top_10_percent` | Among the 10% most cited works of the same field and year. |
| `is_top1` | boolean | `citation_normalized_percentile.is_in_top_1_percent` | Among the 1% most cited works of the same field and year. |
| `n_countries` | integer | `countries_distinct_count` | Number of distinct countries in the author affiliations. |
| `n_institutions` | integer | `institutions_distinct_count` | Number of distinct institutions in the author affiliations. |
| `is_international` | boolean | derived: `n_countries > 1` | International collaboration. |

## `work_universities`

| Column | Type | Description |
|---|---|---|
| `work_id` | text | OpenAlex work ID (foreign key to `works`). |
| `university` | text | `UDC`, `USC` or `UVIGO`. |

A work is assigned to a university when at least one author is affiliated with it or with one of its child institutions (OpenAlex filter `authorships.institutions.lineage`). This is **full counting**: a co-authored work counts once for each university.

## `collab_countries`

| Column | Type | Description |
|---|---|---|
| `university` | text | `UDC`, `USC` or `UVIGO`. |
| `year` | integer | Publication year. |
| `country_code` | text | ISO 3166-1 alpha-2 code of the co-author country, e.g. `US`. Note that `NA` is Namibia, not a missing value. |
| `country_name` | text | Country name, e.g. `United States`. |
| `n_works` | integer | Articles and reviews of the university that year with at least one author from that country. |
| `extracted_on` | text | Date of the OpenAlex counts (`YYYY-MM-DD`). |

Primary key: (`university`, `year`, `country_code`). Spain (`ES`) is included: its `n_works` equals the university's total for that year, which makes it a convenient denominator. Exclude it to list foreign partners only.

## `collab_institutions`

| Column | Type | Description |
|---|---|---|
| `university` | text | `UDC`, `USC` or `UVIGO`. |
| `year` | integer | Publication year. |
| `institution_id` | text | OpenAlex ID of the co-author institution (foreign key to `institutions`). |
| `n_works` | integer | Articles and reviews of the university that year with at least one author from that institution **or any of its child institutions** (OpenAlex `authorships.institutions.lineage`). |
| `n_works_direct` | integer | Same, counting only authors **directly affiliated** with the institution (OpenAlex `authorships.institutions.id`). `0` means the institution is reached only through the lineage of others. |
| `extracted_on` | text | Date of the OpenAlex counts (`YYYY-MM-DD`). |

Primary key: (`university`, `year`, `institution_id`). The two counts answer different questions. `n_works` treats large organisations as a whole (a work with any CSIC institute counts for CSIC), but also credits parent bodies that are not research partners, such as a ministry above CSIC. `n_works_direct` counts only the affiliation written on the paper, so those parent bodies drop to zero or close to it. Comparing both is how umbrella bodies are identified (see "Notes on data quality"). The university itself is included: its `n_works` is the total for that year.

## `institutions`

| Column | Type | Source field in OpenAlex | Description |
|---|---|---|---|
| `institution_id` | text | `id` (URL prefix removed) | OpenAlex institution ID, e.g. `I134820265`. Primary key. |
| `name` | text | `display_name` | Institution name. |
| `type` | text | `type` | `education`, `healthcare`, `facility`, `government`, `company`, `nonprofit`, `funder`, `archive` or `other`. |
| `country_code` | text | `country_code` | ISO 3166-1 alpha-2 country code. |
| `city` | text | `geo.city` | City. |
| `latitude` | float | `geo.latitude` | Latitude. |
| `longitude` | float | `geo.longitude` | Longitude. |

## Notes on data quality

- **Missing values.** Some fields can be empty: conference papers without a `source`, recent works without `fwci` or percentile yet, and works without a `primary_topic`. They are kept as missing (`NULL`), not replaced with zeros.
- **Skewed citation indicators.** Citations and FWCI are highly skewed: a single mega-collaboration paper can have an FWCI of several hundred. Robust indicators (median, % top 10%, % top 1%) are preferred over the mean FWCI.
- **Reviews.** OpenAlex classifies many reviews as `article`, so reviews are analysed together with articles rather than separately.
- **Coverage.** OpenAlex indexes far more content than Web of Science or Scopus, so absolute counts are higher than in those databases. Only articles, reviews and conference papers are included (see README, "Methodology").
- **Lineage and parent bodies.** Grouping institutions by lineage moves each work up the whole hierarchy, so bodies that do not do research themselves can appear as partners (for example a ministry above CSIC, or a regional health service above its hospitals). The institution `type` does not separate them reliably (`government` includes both a ministry and CNRS, a major research organisation), so `n_works_direct` is used instead: parent bodies have few or no direct affiliations.
- **Mega-collaborations.** A single paper from a large consortium can add hundreds of partner institutions in one year. The number of works shared with each partner is robust to this; the number of distinct partner institutions is not.
- **Snapshot dates.** The collaboration counts were downloaded later than the works, and OpenAlex keeps adding records, so yearly totals in `collab_countries` (Spain) can be slightly higher than in `works`. `extracted_on` records the date.
