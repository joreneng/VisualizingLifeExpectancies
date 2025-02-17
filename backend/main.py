from fastapi import FastAPI, HTTPException, Query
from fastapi.logger import logger
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List
from backend.queries import (query_and_process_wealth_health_values, query_and_process_avg_values, BubbleObject,
                             query_and_process_death_causes, find_life_expectancy_of_countries_by_years, DeathCauseData,
                             LineChartData)
from backend.load_db import load_db

app = FastAPI()
load_db()

# Allow CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoint to fetch the average values
@app.get("/chloro-chart-data/{start_year}/{end_year}", response_model=Dict[str, float])
async def get_chloro_chart_data(start_year: int, end_year: int):
    try:
        logger.debug(f"Received request for chloro chart years: {start_year}-{end_year}")

        data = query_and_process_avg_values(start_year, end_year)
        if not data:
            logger.warning("No data returned from chloro chart query")
            raise HTTPException(status_code=404, detail="No data found for the specified years")

        logger.debug(f"First country data: {list(data.items())[:1]}")
        return data
    except Exception as e:
        logger.error(f"Error in chloro_chart: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bubble-data/{start_year}/{end_year}", response_model=Dict[int, List[BubbleObject]])
async def get_bubble_data(start_year: int, end_year: int):
    try:
        logger.debug(f"Received request for years: {start_year}-{end_year}")

        data = query_and_process_wealth_health_values(start_year, end_year)
        if not data:
            logger.warning("No data returned from query")
            raise HTTPException(status_code=404, detail="No data found for the specified years")

        logger.debug(f"First country data: {list(data.items())[:1]}")
        return data
    except Exception as e:
        logger.error(f"Error in bubble_data: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bar-chart-data/{start_year}/{end_year}", response_model=List[DeathCauseData])
async def get_bar_chart_data(start_year: int, end_year: int):
    try:
        logger.debug(f"Fetching death causes for years: {start_year}-{end_year}")
        data = query_and_process_death_causes(start_year, end_year)
        if not data:
            logger.warning("No death causes data found")
            raise HTTPException(status_code=404, detail="No data found for the specified years")
        return data
    except Exception as e:
        logger.error(f"Error in bar_chart: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/line-chart-data/{start_year}/{end_year}", response_model=List[LineChartData])
async def get_line_chart_data(start_year: int, end_year: int):
    try:
        logger.debug(f"Fetching life expectancies of countries by years: {start_year}-{end_year}")
        data = find_life_expectancy_of_countries_by_years(start_year, end_year)
        if not data:
            logger.warning("No life expectancies data found")
            raise HTTPException(status_code=404, detail="No data found for the specified years")
        return data
    except Exception as e:
        logger.error(f"Error in life expectancies: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
