-- Check: top 20 sources of UDC works classified as diamond OA
-- (articles and reviews only, same population as 03_open_access_by_route.sql).

SELECT
    w.source_name,
    w.publisher,
    w.issn_l,
    COUNT(*) AS n_works
FROM work_universities AS wu
JOIN works AS w
    ON w.work_id = wu.work_id
WHERE w.type IN ('article', 'review') 
  AND wu.university = 'UDC' 
  AND w.oa_status = 'diamond'
GROUP BY w.source_name
ORDER BY n_works DESC
LIMIT 20;