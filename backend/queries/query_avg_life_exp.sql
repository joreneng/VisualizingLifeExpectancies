SELECT country_id, AVG(value) AS avg_value
FROM databank
WHERE indicator_id = ?
  AND date BETWEEN ? AND ?
GROUP BY country_id;