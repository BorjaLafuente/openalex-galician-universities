-- Check: is UDC's rise in international collaboration in 2024-2025 real, or
-- an effect of the last years being incomplete or of a change in the mix of
-- publications?
--
-- Two possible biases:
--   1. Indexing lag: articles in small Spanish and Galician journals, which
--      are rarely international, can reach OpenAlex months later than those
--      in large international journals. If they are still missing for 2025,
--      the share of local-language works falls and the international share
--      is inflated.
--   2. Composition: fewer works in local languages means fewer works with
--      little chance of international co-authorship.
-- If the international share also rises among English-language works only,
-- the rise is not explained by either bias.

SELECT
    w.year,
    COUNT(*) AS n_works,

    -- Share of works in Spanish, Galician or Portuguese
    ROUND(AVG(CASE WHEN w.language IN ('es', 'gl', 'pt') THEN 1 ELSE 0 END) * 100, 1)
        AS pct_local_language,

    -- International share of all works (should match sql/04)
    ROUND(AVG(w.is_international) * 100, 1) AS pct_int_all,

    -- Number of works in English
    SUM(CASE WHEN w.language = 'en' THEN 1 ELSE 0 END) AS n_english,

    -- Number of works with no language assigned yet. IS NULL, not = NULL:
    -- NULL means "unknown", and a comparison with an unknown value is never
    -- true
    SUM(CASE WHEN w.language IS NULL THEN 1 ELSE 0 END) AS n_no_language,

    -- International share among English-language works only. CASE without
    -- ELSE gives NULL for the other languages, and AVG ignores NULLs, so the
    -- average is computed over English-language works only.
    ROUND(AVG(CASE WHEN w.language = 'en' THEN w.is_international END) * 100, 1)
        AS pct_int_english
FROM work_universities AS wu
JOIN works AS w
    ON w.work_id = wu.work_id
WHERE wu.university = 'UDC'
  AND w.type IN ('article', 'review')
GROUP BY w.year
ORDER BY w.year;