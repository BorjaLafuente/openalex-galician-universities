-- Check: is the "top 10%" flag consistent with FWCI?
-- If it is, works flagged as top 10% should have clearly high FWCI values.
-- All universities together (articles and reviews with an FWCI value).

SELECT
    w.is_top10,
    COUNT(*)                                                      AS n_works,
    MIN(w.fwci)                                                   AS min_fwci,
    ROUND(AVG(w.fwci), 2)                                         AS avg_fwci,
    ROUND(AVG(CASE WHEN w.fwci < 1 THEN 1 ELSE 0 END) * 100, 1)   AS pct_fwci_below_1
FROM works AS w
WHERE w.type IN ('article', 'review') 
  AND w.fwci IS NOT NULL 
GROUP BY w.is_top10;