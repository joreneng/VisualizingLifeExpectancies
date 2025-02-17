import sqlite3
from typing import Optional, List, Dict
import json

import pandas as pd
from pydantic import BaseModel, StrictStr, StrictInt

from backend.db_setup import connect_db, commit_and_close_db
from backend.config import INDICATORS


class BubbleObject(BaseModel):
    name: str
    region: str
    health_exp: Optional[float] = None
    population: Optional[float] = None
    life_exp: Optional[float] = None

# Helper to remove non-country codes from iso2_codes before I discovered a regions database online
def keep_only_country_codes():
    country_ids_to_delete = ['EU', 'OE', 'XC', 'XD', 'XE', 'XF', 'XG', 'XH', 'XI',
                             'XJ', 'XL', 'XM', 'XN', 'XO', 'XP', 'XQ', 'XT', 'XU', 'PS'
                             'XY', 'ZB', 'ZF', 'ZG', 'ZH', 'ZI', 'ZJ', 'ZQ', 'ZT']
    country_ids_str = ', '.join(f"'{country_id}'" for country_id in country_ids_to_delete)

    conn, cur = connect_db()
    delete_query = f"""
    DELETE FROM country_codes
    WHERE id IN ({country_ids_str})
    OR id GLOB '*[0-9]*';
    """
    cur.execute(delete_query)
    commit_and_close_db(conn)

class LineChartData(BaseModel):
    name: str
    date: int
    value: float

def find_life_expectancy_of_countries_by_years(start_year = 1960, end_year = 2023) -> List[Dict]:
    conn, cur = connect_db()
#     query = """
#     WITH RECURSIVE years(year) AS (
#     SELECT ?
#     UNION ALL
#     SELECT year + 1
#     FROM years
#     WHERE year < ?
# ),
# life_expectancy_data AS (
#     SELECT c.country, d.country_id, d.date, d.value
#     FROM databank d
#     JOIN country_codes c ON d.country_id = c.id
#     WHERE d.indicator_id = 'SP.DYN.LE00.IN' AND
#           d.date BETWEEN (SELECT MIN(year) FROM years)
#               AND (SELECT MAX(year) FROM years)
# ),
#     all_years AS (
#         SELECT c.country_id, c.country, y.year
#         FROM years y
#                  CROSS JOIN (SELECT DISTINCT country_id, country FROM life_expectancy_data) c
# )
# SELECT ay.country, ay.year, le.value
#   FROM all_years ay
# LEFT JOIN life_expectancy_data le
#     ON ay.country_id = le.country_id AND ay.year = le.date
# ORDER BY ay.country_id, ay.year;
# """

    query = """
            SELECT c.country, d.date, d.value
    FROM databank d
    JOIN country_codes c ON d.country_id = c.id
    WHERE d.indicator_id = 'SP.DYN.LE00.IN' AND
          d.date BETWEEN ? AND ?
    GROUP BY d.country_id, d.date;
        """
    cur.execute(query, (start_year, end_year))
    results = cur.fetchall()
    conn.close()

    # date = [{name: 'United Arab Emirates', date: 1960, value: 48.8}]
    data = [
        {
            "name": row[0],
            "date": row[1],
            "value": row[2],
        }
        for row in results
    ]

    return data

# Helper function to query the database and get the average values
def query_and_process_avg_values(start_year = 1960, end_year = 2023) -> Dict[str, float]:
    conn, cur = connect_db()
    query = """
        SELECT country_id, AVG(value) AS avg_value
        FROM databank
        WHERE indicator_id = ?
        AND date BETWEEN ? AND ?
        GROUP BY country_id;
    """
    cur.execute(query, (INDICATORS["LIFE_EXPECTANCY"], start_year, end_year))
    results = cur.fetchall()
    
    data = {row[0]: row[1] for row in results}
    conn.close()
    return data

def query_and_process_wealth_health_values(start_year = 1960, end_year = 2023) -> Dict[int, List[BubbleObject]]:
    conn, cur = connect_db()
    query = """
        SELECT r.country_name, r.region, d.date,
               MAX(CASE WHEN d.indicator_id = "SP.POP.TOTL" THEN d.value END) AS population,
               MAX(CASE WHEN d.indicator_id = "SH.XPD.CHEX.GD.ZS" THEN d.value END) AS health_exp,
               MAX(CASE WHEN d.indicator_id = "SP.DYN.LE00.IN" THEN d.value END) AS life_exp
        FROM databank d
        JOIN regions r ON d.country_id = r.country_id
        WHERE d.indicator_id IN ("SP.POP.TOTL", "SH.XPD.CHEX.GD.ZS", "SP.DYN.LE00.IN")
            AND d.date BETWEEN ? AND ?
        GROUP BY r.country_name, r.region, d.date
        ORDER BY d.date, r.country_name;    
    """
    
    cur.execute(query, (start_year, end_year))
    rows = cur.fetchall()
    
    data = {year: [] for year in range(start_year, end_year + 1)}
    for row in rows:
        data[row[2]].append({
            "name": row[0],
            "region": row[1],
            "population": row[3],
            "health_exp": row[4],
            "life_exp": row[5]
        })
    
    conn.close()
    return data

class DeathCauseData(BaseModel):
    date: int
    name: str
    value: float
    rank: int

def query_and_process_death_causes(start_year = 1960, end_year = 2023) -> List[Dict]:
    conn, cur = connect_db()
    query = """
    SELECT
    d.date,
    CASE 
            WHEN d.indicator_id = 'SH.DTH.COMM.ZS' THEN 'Communicable Diseases'
            WHEN d.indicator_id = 'SH.DTH.INJR.ZS' THEN 'Injuries'
            WHEN d.indicator_id = 'SH.DTH.NCOM.ZS' THEN 'Non-communicable Diseases'
            END AS name,
    avg(d.value) AS avg_percentage_of_total_deaths,
    ROW_NUMBER() OVER (PARTITION BY d.date ORDER BY SUM(d.value) DESC) AS rank
FROM
    databank d
WHERE d.date BETWEEN ? AND ?
            AND d.indicator_id IN (
                'SH.DTH.COMM.ZS' ,  -- Communicable diseases
                'SH.DTH.INJR.ZS',  -- Injuries
                'SH.DTH.NCOM.ZS'   -- Non-communicable diseases
            )
GROUP BY
    d.date, d.indicator_id
ORDER BY
    d.date, rank DESC;
    """
    
    cur.execute(query, (start_year, end_year))
    rows = cur.fetchall()
    
    data = [
        {
            "date": row[0],
            "name": row[1],
            "value": row[2],
            "rank": row[3]
        }
        for row in rows
    ]
    
    conn.close()
    return data
