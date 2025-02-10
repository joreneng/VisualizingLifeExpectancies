import sqlite3
import pandas as pd
import requests
from pydantic import BaseModel, StrictInt, StrictStr


# Validation of params for Databank API
# For better validation:
# Indicator is in the right format, use regex
# Start year is lesser than end year and have 4 digits
# Country code is part of the accepted country codes
class APIParams(BaseModel):
    indicator_id: StrictStr
    start_year: StrictInt
    end_year: StrictInt

    def construct_url(self):
        return f'https://api.worldbank.org/v2/country/all/indicator/{self.indicator_id}?date={self.start_year}:{self.end_year}&format=json'


def create_table():
    con = sqlite3.connect("databank.db")
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS databank "
                "(id INTEGER PRIMARY KEY, date TEXT, indicator_id TEXT, country_id TEXT, value REAL)")
    con.commit()
    con.close()


def fetch_data(indicator_id, start_year, end_year):
    all_data, page = [], 1
    params = APIParams(indicator_id=indicator_id, start_year=start_year, end_year=end_year)
    api_url = params.construct_url()
    response = requests.get(api_url,
                            params={"page": page})
    if len(response.json()) == 1:
        raise Exception("No data found")
    else:
        pages = response.json()[0]['pages']

    while page <= pages:
        data = requests.get(api_url,
                            params={"page": page}).json()
        all_data.extend(data[1])
        page += 1

    return all_data