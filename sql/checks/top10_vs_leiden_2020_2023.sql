-- Check: % of works in the top 10% per university for 2020-2023 combined,
-- to compare with the CWTS Leiden Ranking Open Edition 2025 (same period).
-- Our figures: full counting, all articles and reviews with an FWCI value,
-- using OpenAlex's own top 10% flag. Leiden: core publications only, with its
-- own field normalisation. Levels are not comparable; the question is
-- whether the ranking of the three universities is the same.

SELECT
    wu.university,
    COUNT(*)                         AS n_works,
    SUM(w.is_top10)                  AS n_top10,
    ROUND(AVG(w.is_top10) * 100, 1)  AS pct_top10
FROM work_universities AS wu
JOIN works AS w
    ON w.work_id = wu.work_id
WHERE w.type IN ('article', 'review')
  AND w.fwci IS NOT NULL
  AND w.year BETWEEN 2020 AND 2023
GROUP BY wu.university
ORDER BY pct_top10 DESC;