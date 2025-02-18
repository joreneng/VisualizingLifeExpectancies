SELECT r.country_name, r.region, d.date,
       MAX(CASE WHEN d.indicator_id = "SP.POP.TOTL" THEN d.value END)       AS population,
       MAX(CASE WHEN d.indicator_id = "SH.XPD.CHEX.GD.ZS" THEN d.value END) AS health_exp,
       MAX(CASE WHEN d.indicator_id = "SP.DYN.LE00.IN" THEN d.value END)    AS life_exp
FROM databank d
         JOIN regions r ON d.country_id = r.country_id
WHERE d.indicator_id IN ("SP.POP.TOTL", "SH.XPD.CHEX.GD.ZS", "SP.DYN.LE00.IN")
  AND d.date BETWEEN ? AND ?
GROUP BY r.country_name, r.region, d.date
ORDER BY d.date, r.country_name;