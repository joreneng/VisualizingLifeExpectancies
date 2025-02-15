from fastapi import FastAPI, HTTPException
from fastapi.logger import logger
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Union, Optional
from backend.queries import query_and_process_wealth_health_values, query_and_process_avg_values, BubbleObject, query_and_process_death_causes
from backend.load_db import load_db

app = FastAPI()
# load_db()

# Allow CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # This allows all domains to access the API. Be careful with this in production.
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods like GET, POST, etc.
    allow_headers=["*"],  # Allows all headers
)

# Endpoint to fetch the average values
@app.get("/avg-values", response_model=Dict[str, float])
async def avg_values():
    data = query_and_process_avg_values()
    return data

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
    # data = query_and_process_wealth_health_values(start_year, end_year)  # Pass the variables directly
    # return data

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.get("/death-causes/{start_year}/{end_year}")
async def death_causes(start_year: int, end_year: int):
    try:
        logger.debug(f"Fetching death causes for years: {start_year}-{end_year}")
        data = query_and_process_death_causes(start_year, end_year)
        if not data:
            logger.warning("No death causes data found")
            raise HTTPException(status_code=404, detail="No data found for the specified years")
        return data
    except Exception as e:
        logger.error(f"Error in death_causes: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
