import sqlite3
from typing import Optional, List

import pandas as pd
from pydantic import BaseModel, StrictStr, StrictInt

from backend.config import DB_PATH


class BubbleObject(BaseModel):
    name: str
    region: str
    health_exp: Optional[float] = None
    population: Optional[float] = None
    life_exp: Optional[float] = None


# queries table and returns the data in a dataframe
def query_table_by_indicator_and_years(indicator_id, start_year, end_year):
    conn = sqlite3.connect(DB_PATH)
    query = f"""
    SELECT * FROM databank
    WHERE indicator_id = "{indicator_id}" AND date BETWEEN {start_year} AND {end_year}
    """
    df = pd.read_sql(query, conn)
    return df

def keep_only_country_codes():
    country_ids_to_delete = ['EU', 'OE', 'XC', 'XD', 'XE', 'XF', 'XG', 'XH', 'XI',
                             'XJ', 'XL', 'XM', 'XN', 'XO', 'XP', 'XQ', 'XT', 'XU', 'PS'
                             'XY', 'ZB', 'ZF', 'ZG', 'ZH', 'ZI', 'ZJ', 'ZQ', 'ZT']
    country_ids_str = ', '.join(f"'{country_id}'" for country_id in country_ids_to_delete)

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    delete_query = f"""
    DELETE FROM country_codes
    WHERE id IN ({country_ids_str})
    OR id GLOB '*[0-9]*';
    """
    cur.execute(delete_query)
    con.commit()
    con.close()

def find_avg_life_expectancy_over_all_years():
    query = """
        SELECT country_id, AVG(value) AS avg_value
    FROM databank d
    WHERE indicator_id = 'SP.DYN.LE00.IN'
    GROUP BY indicator_id, country_id;
    """

def find_life_expectancy_of_country(country_id):
    query = f"""
            SELECT country_id, value AS avg_value
        FROM databank d
        WHERE indicator_id = 'SP.DYN.LE00.IN' 
        AND country_id = {country_id};
        """

# Define the structure of the data being returned
class AvgLifeExpectancy(BaseModel):
    country_id: StrictStr
    avg_value: float
    start_year: StrictInt
    end_year: StrictInt

# Helper function to query the database and get the average values
def query_and_process_avg_values(start_year = None, end_year = None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query = """
                SELECT country_id, AVG(value) AS avg_value
                FROM databank
                WHERE indicator_id = 'SP.DYN.LE00.IN'
                GROUP BY country_id;
                """
    if start_year and end_year and start_year <= end_year:
        query = """
            SELECT country_id, AVG(value) AS avg_value
            FROM databank
            WHERE indicator_id = 'SP.DYN.LE00.IN'
            AND date BETWEEN ? AND ?
            GROUP BY country_id;
            """
        cursor.execute(query, (start_year, end_year))
    else:
        cursor.execute(query)

    results = cursor.fetchall()

    # Format the result to return country_id -> avg_value
    data = {}
    for row in results:
        country_id = row[0]
        avg_value = row[1]
        data[country_id] = avg_value

    conn.close()
    return data

def query_and_process_wealth_health_values(start_year, end_year):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query = """
            SELECT r.country_name, r.region, d.date,
                   MAX(CASE WHEN d.indicator_id = 'SP.POP.TOTL' THEN d.value END) AS population,
                   MAX(CASE WHEN d.indicator_id = 'SH.XPD.CHEX.GD.ZS' THEN d.value END) AS health_exp,
                   MAX(CASE WHEN d.indicator_id = 'SP.DYN.LE00.IN' THEN d.value END) AS life_exp
            FROM databank d
            JOIN regions r ON d.country_id = r.country_id
            WHERE d.indicator_id IN ('SP.POP.TOTL', 'SH.XPD.CHEX.GD.ZS', 'SP.DYN.LE00.IN')
                AND d.date BETWEEN ? AND ?
            GROUP BY r.country_name, r.region, d.date
            ORDER BY d.date, r.country_name;    
    """

    cursor.execute(query, (start_year, end_year))
    rows = cursor.fetchall()

    # Initialize the data dictionary with empty lists for each year
    data = {year: [] for year in range(start_year, end_year + 1)}
    
    # Transform into year-based dictionary
    for row in rows:
        name, region, date, population, health_exp, life_exp = row
        
        # Append the country data to the appropriate year's list
        data[date].append({
            "name": name,
            "region": region,
            "health_exp": health_exp,
            "life_exp": life_exp,
            "population": population
        })

    conn.close()
    return data

def query_and_process_death_causes(start_year, end_year):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = """
    WITH ranked_causes AS (
        SELECT 
            d.date,
            r.country_name as name,
            r.region as category,  -- Using region as category for color grouping
            d.indicator_id,
            d.value,
            RANK() OVER (
                PARTITION BY d.date 
                ORDER BY d.value DESC
            ) as rank
        FROM databank d
        JOIN regions r ON d.country_id = r.country_id
        WHERE d.date BETWEEN ? AND ?
            AND d.indicator_id IN (
                'SH.DTH.COMM.ZS',  -- Communicable diseases
                'SH.DTH.INJR.ZS',  -- Injuries
                'SH.DTH.NCOM.ZS'   -- Non-communicable diseases
            )
    )
    SELECT 
        date,
        name,
        category,
        value
    FROM ranked_causes
    WHERE rank <= 12  -- Get top 12 for each year
    ORDER BY date, value DESC;
    """
    
    cursor.execute(query, (start_year, end_year))
    rows = cursor.fetchall()
    
    # Transform into the required format
    data = [
        {
            "date": row[0],
            "name": row[1],
            "category": row[2],
            "value": row[3]
        }
        for row in rows
    ]
    
    conn.close()
    return data