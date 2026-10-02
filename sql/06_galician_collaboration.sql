-- Collaboration between the three Galician universities: number of works
-- co-authored by each pair of universities, per year (articles and reviews only).
-- A work shared by all three universities counts once for each of the three pairs.
-- Self-join on work_universities: the condition a.university < b.university
-- keeps each pair once (UDC-USC, not also USC-UDC) and drops self-pairs.

SELECT
    a.university   AS uni_a, 
    b.university   AS uni_b, 
    w.year,
    COUNT(*)       AS n_shared
FROM work_universities AS a
JOIN work_universities AS b
    ON a.work_id = b.work_id
   AND a.university < b.university
JOIN works AS w
    ON w.work_id = a.work_id
WHERE w.type IN ('article', 'review')
GROUP BY a.university, b.university, w.year
ORDER BY a.university, b.university, w.year;