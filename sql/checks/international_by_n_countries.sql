-- Check: distribution of articles and reviews by number of countries,
-- to see whether the 2024-2025 rise in international collaboration comes
-- from mega-collaborations or from small-scale collaboration.

SELECT
    wu.university,
    w.year,
    COUNT(*)                                                                                     AS n_art_rev,
    ROUND(AVG(CASE WHEN w.n_countries = 1 THEN 1 ELSE 0 END) * 100, 1)                           AS pct_1,
    ROUND(AVG(CASE WHEN w.n_countries = 2 THEN 1 ELSE 0 END) * 100, 1)                           AS pct_2,
    ROUND(AVG(CASE WHEN w.n_countries >= 3 AND w.n_countries <= 5 THEN 1 ELSE 0 END) * 100, 1)   AS pct_3_5,
    ROUND(AVG(CASE WHEN w.n_countries >= 6 AND w.n_countries <= 20 THEN 1 ELSE 0 END) * 100, 1)  AS pct_6_20,
    ROUND(AVG(CASE WHEN w.n_countries > 20 THEN 1 ELSE 0 END) * 100, 1)                          AS pct_21plus
FROM work_universities AS wu
JOIN works AS w
    ON w.work_id = wu.work_id
WHERE w.type IN ('article', 'review') AND w.year >= 2021
GROUP BY wu.university, w.year
ORDER BY wu.university, w.year;