from pathlib import Path
from typing import Optional, List, Dict, Tuple

from fastapi import HTTPException
from pydantic import BaseModel
from starlette import status

from backend.config import INDICATORS
from backend.db.setup import connect_db


class BubbleObject(BaseModel):
    name: str
    region: str
    health_exp: Optional[float] = None
    population: Optional[float] = None
    life_exp: Optional[float] = None


class LineChartData(BaseModel):
    name: str
    date: int
    value: float


class DeathCauseData(BaseModel):
    date: int
    name: str
    value: float
    rank: int


# Function to execute SQL script
def execute_sql_script(file_name: str, start_year: int, end_year: int, indicator_id=None) -> List[
    Tuple[str, int, float]]:
    current_dir = Path(__file__).parent
    sql_path = str(current_dir.parent / "queries" / file_name)
    conn, cur = connect_db()
    try:
        with open(sql_path, 'r') as f:
            sql_script = f.read()

        if indicator_id:
            cur.execute(sql_script, (indicator_id, start_year, end_year))
        else:
            cur.execute(sql_script, (start_year, end_year))

        results = cur.fetchall()
        cur.close()
        conn.close()
        return results

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error executing SQL script: {str(e)}")


def query_and_process_life_expectancies(start_year=1960, end_year=2023) -> List[LineChartData]:
    results = execute_sql_script("query_life_exp.sql", start_year, end_year)

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


# Function to query the database and get the average values
def query_and_process_avg_life_exp(start_year=1960, end_year=2023) -> Dict[str, float]:
    results = execute_sql_script("query_avg_life_exp.sql",
                                 start_year, end_year, INDICATORS["LIFE_EXPECTANCY"])

    data = {row[0]: row[1] for row in results}
    return data


# Function to query the database and get population, health expenditures and life expectancies
def query_and_process_wealth_health_values(start_year=1960, end_year=2023) -> Dict[int, List[BubbleObject]]:
    results = execute_sql_script("query_wealth_health.sql", start_year, end_year)

    data = {year: [] for year in range(start_year, end_year + 1)}
    for row in results:
        data[row[2]].append({
            "name": row[0],
            "region": row[1],
            "population": row[3],
            "health_exp": row[4],
            "life_exp": row[5]
        })
    return data


# Function to query the database and get ranked causes of death
def query_and_process_death_causes(start_year=1960, end_year=2023) -> List[DeathCauseData]:
    results = execute_sql_script("query_death_causes.sql", start_year, end_year)

    data = [
        {
            "date": row[0],
            "name": row[1],
            "value": row[2],
            "rank": row[3]
        }
        for row in results
    ]
    return data
