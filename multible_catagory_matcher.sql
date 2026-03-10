-- multible_catagory_matcher.sql
--
-- Purpose: Find results that match a specific set of category IDs
--          (returns only results that have a 'yes' match for every
--           category listed in `wanted_categories`).
--
-- Usage:
--   Open this file in a SQLite client (e.g., DB Browser for SQLite)
--   and run it against the database containing `result`,
--   `result_category`, and `category` tables. Modify the
--   `INSERT INTO wanted_categories` values to change the target set.
--
-- Notes:
--   - The script creates a temporary table `wanted_categories` and
--     selects results that match all listed categories.
--   - Back up your database before running scripts that modify data.
--
DROP TABLE IF EXISTS wanted_categories;

CREATE TEMP TABLE wanted_categories (
    category_id INTEGER PRIMARY KEY
);

INSERT INTO wanted_categories (category_id) VALUES
(13), (2), (1), (7);

WITH matched_results AS (
    SELECT
        rc.result_id
    FROM result_category rc
    WHERE rc.match = 'yes'
      AND rc.category_id IN (
          SELECT category_id FROM wanted_categories
      )
    GROUP BY rc.result_id
    HAVING COUNT(DISTINCT rc.category_id) =
           (SELECT COUNT(*) FROM wanted_categories)
)
SELECT
    r.result_id,
    r.wayback_url,
    GROUP_CONCAT(c.category_name, ', ') AS matched_categories
FROM matched_results m
JOIN result r
  ON r.result_id = m.result_id
JOIN result_category rc
  ON rc.result_id = m.result_id
JOIN category c
  ON c.category_id = rc.category_id
WHERE rc.match = 'yes'
  AND rc.category_id IN (
      SELECT category_id FROM wanted_categories
  )
GROUP BY
    r.result_id,
    r.wayback_url;
