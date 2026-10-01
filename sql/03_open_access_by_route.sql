-- Open access share per university and year by route (articles and reviews only).
-- Full counting: a work shared by two universities counts for both.

SELECT
    wu.university,
    w.year,
    COUNT(*)                                                                 AS n_works,
    ROUND(AVG(CASE WHEN w.oa_status = 'gold' THEN 1 ELSE 0 END) * 100, 1)    AS pct_gold,
    ROUND(AVG(CASE WHEN w.oa_status = 'diamond' THEN 1 ELSE 0 END) * 100, 1) AS pct_diamond,
    ROUND(AVG(CASE WHEN w.oa_status = 'hybrid' THEN 1 ELSE 0 END) * 100, 1)  AS pct_hybrid,
    ROUND(AVG(CASE WHEN w.oa_status = 'bronze' THEN 1 ELSE 0 END) * 100, 1)  AS pct_bronze,
    ROUND(AVG(CASE WHEN w.oa_status = 'green' THEN 1 ELSE 0 END) * 100, 1)   AS pct_green,
    ROUND(AVG(CASE WHEN w.oa_status = 'closed' THEN 1 ELSE 0 END) * 100, 1)  AS pct_closed
FROM work_universities AS wu
JOIN works AS w
    ON w.work_id = wu.work_id
WHERE w.type IN ('article', 'review')
GROUP BY wu.university, w.year
ORDER BY wu.university, w.year;