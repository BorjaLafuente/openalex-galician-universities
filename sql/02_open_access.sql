-- Open access share per university and year (articles and reviews only).
-- Full counting: a work shared by two universities counts for both.

SELECT
    wu.university,
    w.year,
    COUNT(*)                     AS n_works,
    SUM(w.is_oa)                 AS n_oa,
    ROUND(AVG(w.is_oa) * 100, 1) AS pct_oa
FROM work_universities AS wu
JOIN works AS w
    ON w.work_id = wu.work_id
WHERE w.type IN ('article', 'review')
GROUP BY wu.university, w.year
ORDER BY wu.university, w.year;