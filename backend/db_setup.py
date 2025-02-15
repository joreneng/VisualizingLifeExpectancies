import sqlite3
import pandas as pd
import requests
from pydantic import BaseModel, StrictInt, StrictStr

from config import DB_PATH


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

def create_table():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
            CREATE TABLE IF NOT EXISTS databank (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        indicator_id TEXT,
        country_id TEXT,
        unit TEXT,
        value REAL
    );
        """)

    cur.execute("""
            CREATE UNIQUE INDEX idx_databank_unique 
        ON databank (indicator_id, country_id, date);
        """)

    con.commit()
    con.close()

def create_and_populate_iso2codes():
    all_data, page = [], 1
    country_url = 'https://api.worldbank.org/v2/country?format=json'
    response = requests.get(country_url, params={"page": page})

    pages = response.json()[0]['pages']
    while page <= pages:
        data = requests.get(country_url, params={"page": page}).json()
        all_data.extend(data[1])
        page += 1

    filter_cols = ['iso2Code', 'name']
    df = pd.DataFrame(all_data, columns=filter_cols)
    df.rename(columns={'iso2Code': 'id', 'name': 'country'}, inplace=True)

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
                CREATE TABLE IF NOT EXISTS iso2_codes (
            id TEXT PRIMARY KEY,
            country TEXT
        );
             """)
    df.to_sql('iso2_codes', con, if_exists='append', index=False)
    con.commit()
    con.close()

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

def fetch_country_codes(con):
    query = "SELECT id FROM country_codes"
    country_codes_df = pd.read_sql(query, con)
    return country_codes_df['id'].tolist()

# removes duplicates and adds only the new rows to the table
def add_new_rows_to_table(new_df, con):
    # filter new_df so that it only contains rows with valid country codes and non-null values
    # country_codes = fetch_country_codes(con)
    new_df = new_df.dropna(subset=['country_id', 'value'])
    # valid_codes = new_df['country_id'].isin(country_codes)
    # new_df = new_df[valid_codes]

    existing_df = pd.read_sql("SELECT * FROM databank", con)

    # left join to find rows in new_df that are not in existing_df and include only the new rows in the new df
    merged_df = pd.merge(new_df, existing_df, on=['indicator_id', 'country_id', 'date'], how='left', indicator=True)
    df_to_insert = merged_df[merged_df['_merge'] == 'left_only'].drop(columns=['_merge'])

    # rename the conflicting columns to remove '_x' and '_y'
    df_to_insert['value'] = df_to_insert['value_x'].fillna(df_to_insert['value_y'])
    df_to_insert['unit'] = df_to_insert['unit_x'].fillna(df_to_insert['unit_y'])

    # drop the old value_x, unit_x, value_y, unit_y columns
    df_to_insert = df_to_insert.drop(columns=['value_x', 'unit_x', 'value_y', 'unit_y'])
    df_to_insert.to_sql('databank', con, if_exists='append', index=False)
    con.commit()
    con.close()

# process data fetched to fit the schema
def process_and_populate_data(indicator_id, start_year, end_year):
    data = fetch_data_by_indicator_and_years(indicator_id, start_year, end_year)

    if not data or isinstance(data, dict):
        raise Exception(f"Error fetching data for {indicator_id} from {start_year} to {end_year}")

    filter = ['indicator_id', 'country_id', 'date', 'value', 'unit']
    df = pd.json_normalize(data, sep='_', max_level=1)[filter]

    if not all(col in df.columns for col in filter):
        raise Exception(f"Data is missing required columns. Expected columns: {filter}")

    con = sqlite3.connect(DB_PATH)
    add_new_rows_to_table(df, con)
    con.close()