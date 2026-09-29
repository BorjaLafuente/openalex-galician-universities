# Data dictionary

The cleaned data is stored in two tables:

- **`works`**: one row per unique publication.
- **`work_universities`**: one row per (publication, university) pair. A paper co-authored by UDC and USC appears once in `works` and twice here.

This avoids duplicating shared publications and models the many-to-many relationship between works and universities.

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

## Notes on data quality

- **Missing values.** Some fields can be empty: conference papers without a `source`, recent works without `fwci` or percentile yet, and works without a `primary_topic`. They are kept as missing (`NULL`), not replaced with zeros.
- **Skewed citation indicators.** Citations and FWCI are highly skewed: a single mega-collaboration paper can have an FWCI of several hundred. Robust indicators (median, % top 10%, % top 1%) are preferred over the mean FWCI.
- **Reviews.** OpenAlex classifies many reviews as `article`, so reviews are analysed together with articles rather than separately.
- **Coverage.** OpenAlex indexes far more content than Web of Science or Scopus, so absolute counts are higher than in those databases. Only articles, reviews and conference papers are included (see README, "Methodology").
