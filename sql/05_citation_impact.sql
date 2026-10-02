-- Citation impact per university and year (articles and reviews only).
-- Full counting: a work shared by two universities counts for both.
-- Citation indicators are highly skewed, so the mean FWCI is reported together
-- with robust indicators: median FWCI and % of works in the top 10% / top 1%.
-- Recent years have a short citation window and are less stable.

-- Step 1: the works to analyse (articles and reviews with an FWCI value)
WITH base AS (
    SELECT
        wu.university,
        w.year,
        w.fwci,
        w.is_top10,
        w.is_top1
    FROM work_universities AS wu
    JOIN works AS w
        ON w.work_id = wu.work_id
    WHERE w.type IN ('article', 'review')
      AND w.fwci IS NOT NULL
),

-- Step 2: number each work within its group, ordered by FWCI.
-- ROW_NUMBER() and COUNT(*) are window functions: OVER (PARTITION BY ...)
-- computes them within each university-year group without collapsing rows.
ranked AS (
    SELECT
        university,
        year,
        fwci,
        ROW_NUMBER() OVER (PARTITION BY university, year ORDER BY fwci) AS rn,
        COUNT(*)     OVER (PARTITION BY university, year)               AS n
    FROM base
),

-- Step 3: the median is the middle value (odd n) or the mean of the two
-- middle values (even n). With integer division, (n + 1) / 2 and (n + 2) / 2
-- point to the same row when n is odd and to the two middle rows when n is even.
medians AS (
    SELECT
        university,
        year,
        AVG(fwci) AS median_fwci
    FROM ranked
    WHERE rn IN ((n + 1) / 2, (n + 2) / 2)
    GROUP BY university, year
)

-- Step 4: combine the usual aggregates with the median
SELECT
    b.university,
    b.year,
    COUNT(*)                        AS n_works,
    ROUND(AVG(b.fwci), 2)           AS mean_fwci,
    ROUND(m.median_fwci, 2)         AS median_fwci,
    ROUND(AVG(b.is_top10) * 100, 1) AS pct_top10,
    ROUND(AVG(b.is_top1) * 100, 1)  AS pct_top1
FROM base AS b
JOIN medians AS m
    ON m.university = b.university
   AND m.year = b.year
-- median_fwci has a single value per group, but it is listed in GROUP BY too
-- so the query also runs on stricter databases (e.g. PostgreSQL).
GROUP BY b.university, b.year, m.median_fwci
ORDER BY b.university, b.year;
