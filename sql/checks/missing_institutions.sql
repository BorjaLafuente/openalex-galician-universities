-- Check: institutions that appear among the co-authors (collab_institutions)
-- but have no record in the institutions table. Expected: 4 IDs, probably
-- institutions merged or deleted in OpenAlex after being counted.

SELECT
    ci.institution_id,
    SUM(ci.n_works) AS total_works
FROM collab_institutions AS ci
LEFT JOIN institutions AS i
    ON ci.institution_id = i.institution_id
WHERE i.institution_id IS NULL
GROUP BY ci.institution_id
ORDER BY total_works DESC;