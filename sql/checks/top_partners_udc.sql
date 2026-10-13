-- Check: top 20 co-author institutions of UDC, 2015-2025 (articles and
-- reviews, full counting). Shows how many of the largest "partners" are
-- parent bodies brought in by the lineage grouping (ministries, health
-- services) rather than research partners. UDC itself is excluded.

SELECT
    i.name,
    i.type,
    i.country_code,
    SUM(ci.n_works) AS total_works,
    SUM(ci.n_works_direct) AS total_direct
FROM collab_institutions AS ci
JOIN institutions AS i
    ON ci.institution_id = i.institution_id
WHERE ci.university = 'UDC'
  AND ci.institution_id != 'I11019714'
GROUP BY ci.institution_id, i.name, i.type, i.country_code
ORDER BY total_works DESC
LIMIT 20;