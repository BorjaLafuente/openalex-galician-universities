-- International collaboration per university and year, with articles/reviews
-- and conference papers reported separately.
-- Full counting: a work shared by two universities counts for both.

SELECT
    wu.university,
    w.year,
    -- Articles and reviews
    COUNT(CASE WHEN w.type IN ('article', 'review') THEN 1 END)                                AS n_art_rev,
    SUM(CASE WHEN w.type IN ('article', 'review') THEN w.is_international END)                 AS n_int_art_rev,
    ROUND(AVG(CASE WHEN w.type IN ('article', 'review') THEN w.is_international END) * 100, 1) AS pct_int_art_rev,
    -- Conference papers
    COUNT(CASE WHEN w.type = 'conference-paper' THEN 1 END)                                    AS n_conf,
    SUM(CASE WHEN w.type = 'conference-paper' THEN w.is_international END)                     AS n_int_conf,
    ROUND(AVG(CASE WHEN w.type = 'conference-paper' THEN w.is_international END) * 100, 1)     AS pct_int_conf
FROM work_universities AS wu
JOIN works AS w
    ON w.work_id = wu.work_id
GROUP BY wu.university, w.year
ORDER BY wu.university, w.year;