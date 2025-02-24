import sqlite3
import pandas as pd
import requests
from pydantic import BaseModel, StrictInt, StrictStr

from backend.config import DB_PATH


# Validation of params for Databank API
# For better validation:
# Indicator is in the right format, use regex
# Start year is lesser than end year and have 4 digits
# Country code is part of the accepted country codes, use comprehensive list of enums
class APIParams(BaseModel):
    indicator_id: StrictStr
    start_year: StrictInt
    end_year: StrictInt

    def construct_url(self):
        return f'https://api.worldbank.org/v2/country/all/indicator/{self.indicator_id}?date={self.start_year}:{self.end_year}&format=json'

def connect_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    return conn, cur

def commit_and_close_db(conn, cur):
    conn.commit()
    cur.close()
    conn.close()

# fetches data from the databank API and returns the queried data in a list of dictionaries
def fetch_data_by_indicator_and_years(indicator_id, start_year, end_year):
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


# removes duplicates and adds only the new rows to the table
def add_new_rows_to_table(new_df):
    # filter new_df so that it only contains rows with non-null values
    new_df = new_df.dropna(subset=['country_id', 'value'])

    conn, cur = connect_db()
    existing_df = pd.read_sql("SELECT * FROM databank", conn)

    # left join to find rows in new_df that are not in existing_df and include only the new rows in the new df
    new_df.loc[:, 'date'] = new_df['date'].astype(int)
    merged_df = pd.merge(new_df, existing_df, on=['indicator_id', 'country_id', 'date'], how='left', indicator=True)
    df_to_insert = merged_df[merged_df['_merge'] == 'left_only'].drop(columns=['_merge'])

    # rename the conflicting columns to remove '_x' and '_y'
    df_to_insert['value'] = df_to_insert['value_x'].fillna(df_to_insert['value_y'])
    df_to_insert['unit'] = df_to_insert['unit_x'].fillna(df_to_insert['unit_y'])

    # drop the old value_x, unit_x, value_y, unit_y columns
    df_to_insert = df_to_insert.drop(columns=['value_x', 'unit_x', 'value_y', 'unit_y'])
    df_to_insert.to_sql('databank', conn, if_exists='append', index=False)
    commit_and_close_db(conn, cur)


# process data fetched to fit the schema
def process_and_populate_data(indicator_id, start_year, end_year):
    data = fetch_data_by_indicator_and_years(indicator_id, start_year, end_year)

    if not data or isinstance(data, dict):
        raise Exception(f"Error fetching data for {indicator_id} from {start_year} to {end_year}")

    filter = ['indicator_id', 'country_id', 'date', 'value', 'unit']
    df = pd.json_normalize(data, sep='_', max_level=1)[filter]

    if not all(col in df.columns for col in filter):
        raise Exception(f"Data is missing required columns. Expected columns: {filter}")

    add_new_rows_to_table(df)