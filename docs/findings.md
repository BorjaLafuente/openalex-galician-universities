# Analysis log: decisions and findings

Running record of methodological decisions, data quality checks and results,
with the script or query that supports each one. The README is built from
this file.

Unless stated otherwise, figures refer to articles and reviews, with full
counting (a work shared by several universities counts for each of them).

---

## 1. Methodology

### Scope
- **Universities** (OpenAlex institution IDs): Universidade da Coruña (UDC, `I11019714`), Universidade de Santiago de Compostela (USC, `I200284239`), Universidade de Vigo (UVIGO, `I6289922`). Source: `src/explore_institutions.py`.
- **Period**: publication years 2015–2025.
- **Affiliation**: a work belongs to a university when at least one author is affiliated with it or with one of its child institutions in the OpenAlex hierarchy (filter `authorships.institutions.lineage`).
- **Counting**: full counting.

### Document types
- **Included**: `article`, `review` and `conference-paper`. These are the types usually considered in research assessment calls. Articles and reviews form the core of the analysis; conference papers are reported separately.
- **Excluded**: preprints, datasets, book chapters, editorials, errata, peer reviews and other minor types.
- **Rationale**: the other types add noise to the yearly series without reflecting research output. For example, UDC has a one-off spike of 115 datasets in 2019, and preprints grow steadily from 12 (2015) to 98 (2025). Source: `src/explore_types.py`.
- **Reviews are grouped with articles**: OpenAlex classifies many reviews as `article` (only 169 UDC reviews in 11 years, far below the usual share in Web of Science), so the distinction is not reliable.

### Download
- 70,959 records downloaded (UDC 15,544; USC 33,709; UVIGO 21,706), matching the counts announced by the API. Source: `src/extract.py`.
- The list of authors (`authorships`) is not downloaded: papers from large physics collaborations list thousands of authors. International collaboration is measured with `countries_distinct_count` instead.

---

## 2. Data quality

### Coverage
- OpenAlex indexes far more content than Web of Science or Scopus, so absolute counts are clearly higher than in those databases (UDC: about 1,700 publications per year, all types). Comparisons should be made within OpenAlex, not against WoS/Scopus figures.

### Shared publications
- The 70,959 records correspond to **66,972 unique works**: 3,987 extra links come from works shared between two or three of the universities. Source: `src/transform.py`.

### Missing values (66,972 unique works)
| Field | Missing | % |
|---|---|---|
| DOI | 3,326 | 5.0 |
| Source (journal/conference) | 3,475 | 5.2 |
| Publisher | 9,293 | 13.9 |
| ISSN-L | 7,457 | 11.1 |
| Subject (domain/field/subfield) | 88 | 0.1 |
| FWCI and citation percentiles | 88 | 0.1 |

- The same 88 works lack both subject classification and FWCI: FWCI is normalised by field, so it cannot be computed without a subject.
- 37 works have ISSNs but no ISSN-L (7,420 vs 7,457 missing): a minor inconsistency in OpenAlex.
- DOI coverage (95%) is the upper limit for matching these records with Web of Science or Scopus.

### Recent years
- 2025 does not look incomplete: it is the year with the highest output for all three universities. Source: `src/explore_counts.py`.

### Citation outliers
- Citation indicators are highly skewed. Example: *Gaia Data Release 2* (2018, with UDC authors) has 8,640 citations, an FWCI of 767, 26 countries and 136 institutions. A single work like this inflates the mean FWCI of a whole university, so robust indicators (median, % top 10%, % top 1%) are preferred.

### Check: diamond open access
- **Question**: diamond OA (open journals with no author fees) accounts for 22–29% of UDC articles every year since 2015, which looked suspiciously high. Hypothesis: journals with unknown APCs wrongly classified as diamond.
- **Check**: top 20 journals of UDC diamond works. Source: `sql/checks/diamond_sources_udc.sql`.
- **Result: the hypothesis is not supported.** The list is dominated by university and scholarly society journals, typical diamond journals: at least 11 of the top 20 are published by UDC itself (about 500 works), led by *Revista de Estudios e Investigación en Psicología y Educación* (192). *Journal of High Energy Physics* is funded by SCOAP3, so it is free for authors. The high diamond share reflects a real feature of the Spanish system (many open, fee-free university journals) and publication in the university's own journals.
- **Pending**: verify the model of *El Profesional de la Información*, *HUMAN REVIEW* and *European Public & Social Innovation Review* (66 works in total).

### Check: rise in international collaboration (2024–2025)
- **Question**: UDC's international collaboration rises 11 points in two years (2023–2025). Is it real, or an artefact of OpenAlex data or of mega-collaborations?
- **Check**: distribution of works by number of countries, 2021–2025. Source: `sql/checks/international_by_n_countries.sql`.
- **Result: the rise appears to be real.**
  - It only happens at UDC: the share of single-country works falls from 62.4% (2023) to 51.8% (2025), while it is stable at USC (51.5–54.7%) and rises slightly at UVIGO (46.3–51.8%). A change in OpenAlex data would affect all three.
  - It is broad-based: all collaboration sizes grow. The largest change is in 6–20 countries, which doubles in 2024 (3.4% → 7.0%), the typical size of European project consortia.
  - Mega-collaborations (more than 20 countries) appear in 2025 (0.2% → 2.2%) and explain about 2 of the 5.4 points gained between 2024 and 2025.

---

## 3. Results

### Output — `sql/01_output_by_year.sql`
- All document types, 2015 → 2025: UDC +48%, USC +47%, UVIGO +67%. Source: `src/explore_counts.py`.
- Articles peak in 2020–2021 and fall in 2022 at UDC (−11%) and USC (−11%), and in 2024 at UVIGO (−10%).
- **UDC has the most engineering-oriented profile**: articles are 72% of its output, compared with 80% at USC and 76% at UVIGO, mainly because of conference papers (2,062, 11% of UDC output).

### Open access — `sql/02_open_access.sql`, `sql/03_open_access_by_route.sql`
- **UDC open access rises from 66.5% (2015) to 89.4% (2022–2024)**, with the largest jump between 2020 and 2022. USC is about 5 points below UDC in 2015–2018.
- OpenAlex uses a broad definition of open access (any free version, including repository copies and free-to-read publisher versions without an open licence), and older years keep rising as repository copies are added. Figures are therefore higher than in WoS or Scopus.
- **By route (UDC)**:
  - **Hybrid** is stable at about 5% until 2020 and then jumps to 15.8% (2021), 24.7% (2022) and 29.3% (2024). The timing matches the CRUE-CSIC transformative agreements with major publishers, in force from 2021.
  - **Gold** grows from 7.0% (2015) to 26.1% (2020) and then stays at 23–27%, consistent with the growth and later plateau of APC-funded open access publishers.
  - **Green** falls from 21.5% to about 8%. This does not mean less repository deposit: OpenAlex assigns each work a single, best route, so works that are also hybrid or gold are not counted as green. Recent years may also rise when embargoes end.
  - **Closed** falls from 33.5% to 10–13%.
  - **Diamond** is stable at 22–29% (see the diamond check above).

### International collaboration — `sql/04_international_collaboration.sql`
- **UDC rises from 29.9% (2015) to 34.5–37.6% (2019–2023), and then to 42.8% (2024) and 48.2% (2025)** (see the check above).
- USC starts higher (37–42% in 2015–2018), consistent with its strong presence in highly internationalised fields such as physics and medicine.
- At UDC, conference papers show international collaboration rates similar to articles (26–40%), with more year-to-year variation.
- Small groups give unstable percentages: for example, USC conference papers jump to 56.4% in 2016, but on only 133 works. Base counts are always reported next to percentages for this reason.

---

## 4. Pending
- Citation impact indicators (`05`): mean and median FWCI, % top 10%, % top 1%.
- Collaboration between the three Galician universities.
- Charts and final write-up.
