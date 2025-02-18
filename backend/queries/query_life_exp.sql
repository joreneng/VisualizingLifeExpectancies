SELECT c.country, d.date, d.value
FROM databank d
         JOIN country_codes c ON d.country_id = c.id
WHERE d.indicator_id = 'SP.DYN.LE00.IN'
  AND d.date BETWEEN ? AND ?
GROUP BY d.country_id, d.date;

-- Query to find country life expectancies for every year and fill in the missing years with null values
-- Ended up not using it because there were no null values
--
--      WITH RECURSIVE years(year) AS (
--         SELECT ?
--         UNION ALL
--         SELECT year + 1
--         FROM years
--         WHERE year < ?
--     ),
--     life_expectancy_data AS (
--         SELECT c.country, d.country_id, d.date, d.value
--         FROM databank d
--         JOIN country_codes c ON d.country_id = c.id
--         WHERE d.indicator_id = 'SP.DYN.LE00.IN' AND
--               d.date BETWEEN (SELECT MIN(year) FROM years)
--                   AND (SELECT MAX(year) FROM years)
--     ),
--         all_years AS (
--             SELECT c.country_id, c.country, y.year
--             FROM years y
--                      CROSS JOIN (SELECT DISTINCT country_id, country FROM life_expectancy_data) c
--     )
--     SELECT ay.country, ay.year, le.value
--       FROM all_years ay
--     LEFT JOIN life_expectancy_data le
--         ON ay.country_id = le.country_id AND ay.year = le.date
--     ORDER BY ay.country_id, ay.year;