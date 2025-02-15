from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict
from queries import get_avg_values

app = FastAPI()

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
    data = get_avg_values()
    return data

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
