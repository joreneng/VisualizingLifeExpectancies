SELECT d.date,
       CASE
           WHEN d.indicator_id = 'SH.DTH.COMM.ZS' THEN 'Communicable Diseases'
           WHEN d.indicator_id = 'SH.DTH.INJR.ZS' THEN 'Injuries'
           WHEN d.indicator_id = 'SH.DTH.NCOM.ZS' THEN 'Non-communicable Diseases'
           END                                                            AS name,
       AVG(d.value)                                                       AS avg_percentage_of_total_deaths,
       ROW_NUMBER() OVER (PARTITION BY d.date ORDER BY AVG(d.value) DESC) AS rank
FROM databank d
WHERE d.date BETWEEN ? AND ?
  AND d.indicator_id IN (
                         'SH.DTH.COMM.ZS', -- Communicable diseases
                         'SH.DTH.INJR.ZS', -- Injuries
                         'SH.DTH.NCOM.ZS' -- Non-communicable diseases
    )
GROUP BY d.date, d.indicator_id
ORDER BY d.date, rank DESC;