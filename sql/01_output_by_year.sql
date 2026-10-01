-- Publications per university and year, split by document group.
-- Full counting: a work shared by two universities counts for both.

SELECT
    wu.university,
    w.year,
    SUM(CASE WHEN w.type IN ('article', 'review') THEN 1 ELSE 0 END) AS articles_reviews,
    SUM(CASE WHEN w.type = 'conference-paper' THEN 1 ELSE 0 END)     AS conference_papers,
    COUNT(*)                                                          AS total
FROM work_universities AS wu
JOIN works AS w
    ON w.work_id = wu.work_id
GROUP BY wu.university, w.year
ORDER BY wu.university, w.year;
