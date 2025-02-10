from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import populate_data

app = FastAPI()


# Ensure the table is created when the application starts
# create_table()

@app.get("/collect-data/{series_name}/{start_year}/{end_year}")
async def collect_data(series_name: str, start_year: int, end_year: int):
    try:
        populate_data(series_name, start_year, end_year)
        return {"message": "Data collected successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
