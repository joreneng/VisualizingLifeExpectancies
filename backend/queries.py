import sqlite3
import pandas as pd
from pydantic import BaseModel, StrictStr, StrictInt

from config import DB_PATH


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
def get_avg_values(start_year = None, end_year = None):
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