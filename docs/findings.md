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
- Publication counts are consistent with the CWTS Leiden Ranking Open Edition, which uses the same source (see "External validation" below).

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

### Check: consistency of the top 10% flag with FWCI
- **Question**: 18–30% of works are flagged as top 10% every year, far above the 10% expected for an average institution, while the median FWCI is below 1. Is the flag consistent with FWCI?
- **Check**: FWCI of works inside and outside the top 10%, all three universities. Source: `sql/checks/top10_vs_fwci.sql`.
- **Result: the flag is internally consistent.** Works flagged as top 10% (15,573 of 61,580, i.e. 25.3%) have a mean FWCI of 8.69, and only 0.2% of them have an FWCI below 1. Works outside the top 10% have a mean FWCI of 0.73.
- **Note on the median**: a median FWCI below 1 does **not** mean that the typical work is below the world average. FWCI averages 1 worldwide, but citations are highly skewed, so the world median is well below 1. A median of 0.8 and a top 10% share of 20% are compatible.
- The high top 10% share is explained by OpenAlex's normalisation method, not by the data (see the next section).

### External validation: CWTS Leiden Ranking Open Edition 2025
The Leiden Ranking Open Edition is built by CWTS from the same source (a full OpenAlex snapshot), with its own methodology. Comparison for 2020–2023, full counting unless stated otherwise. This project: articles and reviews; Leiden: its own selection of publications. Source: Leiden Ranking Open Edition 2025 data; `sql/checks/top10_vs_leiden_2020_2023.sql`.

**Publication counts (all publications)**

| | Leiden | This project | Difference |
|---|---|---|---|
| UDC | 5,315 | 5,232 | −1.6% |
| UVIGO | 8,100 | 8,513 | +5.1% |
| USC | 10,987 | 12,286 | +11.8% |

- UDC and UVIGO match closely, which validates the extraction (affiliation filter, document types and deduplication).
- USC has about 1,300 more works here. Likely cause: the `lineage` filter includes all child institutions in the OpenAlex hierarchy, and USC has more of them (research institutes, possibly health-related centres), while CWTS uses its own affiliation criteria. Not verified.

**International collaboration and open access (UDC, all publications)**
- International collaboration: 39.2% (Leiden) vs about 36.6% here. Consistent.
- Open access by route: hybrid 18.5% vs about 17.7%, bronze 5.5% vs about 5.4%, green 9.1% vs about 11.8%. Leiden has no diamond category: its gold (42.1%) includes diamond, compared with about 50% gold + diamond here. Total open access: 75.2% vs about 85%. The difference is concentrated in gold/diamond, probably because CWTS uses a different version of the open access data.

**Citation impact**

| | This project (all works, full) | Leiden core, full counting | Leiden core, fractional counting |
|---|---|---|---|
| PP(top 10%) UVIGO | 28.1% | 15.3% | 11.5% |
| PP(top 10%) USC | 24.4% | 13.1% | 9.9% |
| PP(top 10%) UDC | 20.6% | 9.5% | 6.9% |
| MNCS UVIGO / USC / UDC | — | 1.4 / 1.3 / 1.0 | 1.1 / 1.0 / 0.8 |

- CWTS only reports normalised impact indicators for core publications (English-language articles and reviews in international journals), so the non-core population cannot be compared.
- **OpenAlex's precomputed impact indicators are about twice as high as CWTS's**: our top 10% share is 2.2 (UDC), 1.9 (USC) and 1.8 (UVIGO) times Leiden's core, full-counting value. Fractional counting explains only part of the gap (UDC: 9.5% → 6.9%).
- **The ranking of the three universities is the same in every impact indicator: UVIGO > USC > UDC.** Relative comparisons are therefore valid.
- **The size of the differences is compressed**: in Leiden (core, fractional) UVIGO's top 10% share is 1.7 times UDC's; here it is only 1.4 times. Results can say which university has higher impact, but not how much higher.

**Why the impact indicators differ.** OpenAlex's FWCI and CWTS's MNCS belong to the same family (actual / expected citations), but:

| | FWCI (OpenAlex) | MNCS (CWTS) |
|---|---|---|
| Field definition | about 250 subfields, plus year and document type | about 4,500 micro-fields built from citation relations, plus year |
| Reference set | all OpenAlex content in the subfield | core publications only |
| Citation window | publication year + 3 years | citations until the end of 2024 |
| Self-citations | included | excluded |

OpenAlex's much broader reference set, which includes a large amount of rarely cited content, lowers the expected number of citations and raises the ratio. Broader fields and the inclusion of self-citations push in the same direction.

---

## 3. Results

### Output — `sql/01_output_by_year.sql`
Figure: `figures/01_output.png`.
- All document types, 2015 → 2025: UDC +48%, USC +47%, UVIGO +67%. Source: `src/explore_counts.py`.
- Articles peak in 2020–2021 and fall in 2022 at UDC (−11%) and USC (−11%), and in 2024 at UVIGO (−10%).
- **UDC has the most engineering-oriented profile**: articles are 72% of its output, compared with 80% at USC and 76% at UVIGO, mainly because of conference papers (2,062, 11% of UDC output).

### Open access — `sql/02_open_access.sql`, `sql/03_open_access_by_route.sql`
Figure: `figures/02_open_access_routes.png`.
- **UDC open access rises from 66.5% (2015) to 89.4% (2022–2024)**, with the largest jump between 2020 and 2022. USC is about 5 points below UDC in 2015–2018.
- OpenAlex uses a broad definition of open access (any free version, including repository copies and free-to-read publisher versions without an open licence), and older years keep rising as repository copies are added. Figures are therefore higher than in WoS or Scopus.
- **By route (UDC)**:
  - **Hybrid** is stable at about 5% until 2020 and then jumps to 15.8% (2021), 24.7% (2022) and 29.3% (2024). The timing matches the CRUE-CSIC transformative agreements with major publishers, in force from 2021.
  - **Gold** grows from 7.0% (2015) to 26.1% (2020) and then stays at 23–27%, consistent with the growth and later plateau of APC-funded open access publishers.
  - **Green** falls from 21.5% to about 8%. This does not mean less repository deposit: OpenAlex assigns each work a single, best route, so works that are also hybrid or gold are not counted as green. Recent years may also rise when embargoes end.
  - **Closed** falls from 33.5% to 10–13%.
  - **Diamond** is stable at 22–29% (see the diamond check above).
- **The jump in hybrid open access from 2021 happens at all three universities at the same time.** A system-wide change of this kind supports the CRUE-CSIC transformative agreements as the main driver, rather than decisions of any single university.

### International collaboration — `sql/04_international_collaboration.sql`
Figure: `figures/03_international_collaboration.png`.
- **UDC rises from 29.9% (2015) to 34.5–37.6% (2019–2023), and then to 42.8% (2024) and 48.2% (2025)** (see the check above).
- USC and UVIGO start higher (USC 37–42% in 2015–2018), consistent with USC's strong presence in highly internationalised fields such as physics and medicine.
- **UVIGO has the highest share for most of the period**, peaking at 53.7% in 2022, and then declines.
- **The three universities converge at about 48% in 2025** (UDC 48.2%, USC 48.5%, UVIGO about 48%): UDC rises sharply while UVIGO falls. UVIGO's decline matches the rise in its single-country works seen in the collaboration-size check (46.3% → 51.8%).
- At UDC, conference papers show international collaboration rates similar to articles (26–40%), with more year-to-year variation.
- Small groups give unstable percentages: for example, USC conference papers jump to 56.4% in 2016, but on only 133 works. Base counts are always reported next to percentages for this reason.

### Citation impact — `sql/05_citation_impact.sql`
Figure: `figures/04_citation_impact.png`.
- Impact indicators are interpreted **only as comparisons between the three universities**, not as absolute levels (see "External validation").
- **The mean FWCI is not reliable on its own**: it is 2 to 4 times the median every year. The most extreme case is UDC in 2016 (mean 4.49, median 1.07), driven by a handful of very highly cited mega-collaboration papers.
- **UDC's median FWCI declines** from 1.05 (2015) to 0.74–0.82 (2021–2024). A possible explanation is a change in composition, such as the growth of publications in Spanish open journals, which receive fewer international citations; this has not been tested.
- **2025 is not reliable** for impact (median 0.55): works published a few months ago have had little time to be cited.
- **Ranking 2020–2023 by share of top 10% works: UVIGO (28.1%) > USC (24.4%) > UDC (20.6%)**, the same order as in the Leiden Ranking.
- **UVIGO is ahead of USC and UDC every year from 2016.** UDC dips to 18–19% in 2022–2023 and recovers to 22.1% in 2024.

### Collaboration between the Galician universities — `sql/06_galician_collaboration.sql`
Figure: `figures/05_galician_collaboration.png`.

Works co-authored by each pair of universities, articles and reviews, 2015–2025. A work shared by all three counts for each of the three pairs.

| Pair | Shared works 2015–2025 | 2015 → 2025 |
|---|---|---|
| USC–UVIGO | 1,775 | 114 → 169 (+48%) |
| UDC–USC | 1,470 | 121 → 184 (+52%) |
| UDC–UVIGO | 644 | 46 → 61 (+33%) |

- **USC is the hub of the Galician system**: it is part of the two strongest pairs. This is consistent with its size and with geography, as Santiago lies between A Coruña (about 70 km) and Vigo (about 90 km).
- **UDC–UVIGO is clearly the weakest pair**, with less than half the shared works of the other two and the slowest growth: about 4–5% of UDC's articles and under 3% of UVIGO's (2021–2025). The larger distance between the two cities (about 160 km) is consistent with this, but it is a correlation, not a tested explanation.
- In relative terms, USC is the main Galician partner of both UDC (11–13% of UDC's articles) and UVIGO (about 8–9% of UVIGO's articles in 2021–2025).
- USC–UVIGO follows the pandemic pattern seen in total output: a peak in 2020–2021 (207 and 206 works) and a drop in 2022 (158).
- UDC–USC jumps in 2025 (144 → 184), the same year as UDC's rise in international collaboration.
- Consistency check: the three pairs add up to 3,889 links for articles and reviews, of the same order as the 3,987 extra links found in `transform.py` for all three document types.

---

## 4. Pending
- Check whether the `lineage` filter explains the extra USC works (compare with `institutions.id`).
- Verify the model of the three journals flagged in the diamond check.
- Final write-up (README).
