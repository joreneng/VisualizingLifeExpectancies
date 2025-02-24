from typing import Dict, List

from fastapi import FastAPI, HTTPException, status
from fastapi.logger import logger
from fastapi.middleware.cors import CORSMiddleware

from backend.db.fetch import (query_and_process_wealth_health_values, query_and_process_avg_life_exp, BubbleObject,
                              query_and_process_death_causes, query_and_process_life_expectancies, DeathCauseData,
                              LineChartData)
from backend.db.load import load_db

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

        data = query_and_process_avg_life_exp(start_year, end_year)
        if not data:
            logger.warning("No data returned from chloro chart query")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No data found for the specified years")

        logger.debug(f"First country data: {list(data.items())[:1]}")
        return data
    except Exception as e:
        logger.error(f"Error in chloro_chart: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get("/bubble-data/{start_year}/{end_year}", response_model=Dict[int, List[BubbleObject]])
async def get_bubble_data(start_year: int, end_year: int):
    try:
        logger.debug(f"Received request for years: {start_year}-{end_year}")

        data = query_and_process_wealth_health_values(start_year, end_year)
        if not data:
            logger.warning("No data returned from query")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No data found for the specified years")

        logger.debug(f"First country data: {list(data.items())[:1]}")
        return data
    except Exception as e:
        logger.error(f"Error in bubble_data: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get("/bar-chart-data/{start_year}/{end_year}", response_model=List[DeathCauseData])
async def get_bar_chart_data(start_year: int, end_year: int):
    try:
        logger.debug(f"Fetching death causes for years: {start_year}-{end_year}")
        data = query_and_process_death_causes(start_year, end_year)
        if not data:
            logger.warning("No death causes data found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No data found for the specified years")
        return data
    except Exception as e:
        logger.error(f"Error in bar_chart: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get("/line-chart-data/{start_year}/{end_year}", response_model=List[LineChartData])
async def get_line_chart_data(start_year: int, end_year: int):
    try:
        logger.debug(f"Fetching life expectancies of countries by years: {start_year}-{end_year}")
        data = query_and_process_life_expectancies(start_year, end_year)
        if not data:
            logger.warning("No life expectancies data found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No data found for the specified years")
        return data
    except Exception as e:
        logger.error(f"Error in life expectancies: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
