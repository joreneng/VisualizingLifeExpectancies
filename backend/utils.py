from pathlib import Path

import pandas as pd
import requests

from backend.db.setup import connect_db, commit_and_close_db

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

    conn, cur = connect_db()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS iso2_codes (
            id TEXT PRIMARY KEY,
            country TEXT
        );
             """)
    df.to_sql('iso2_codes', conn, if_exists='append', index=False)
    commit_and_close_db(conn, cur)


def create_and_populate_regions ():
    current_dir = Path(__file__).parent
    json_path = str(current_dir.parent / "data" / "countries_with_region.json")
    df = pd.read_json(json_path)
    df.rename(columns={'alpha-2': 'country_id',
                       'name': 'country_name', 'sub-region': 'sub_region'}, inplace=True)
    cols = ['country_id', 'country_name', 'region', 'sub_region']
    df_to_insert = df[cols]
    df_to_insert = df_to_insert.dropna(subset=['country_id', 'country_name', 'region', 'sub_region'])

    conn, cur = connect_db()
    query = ("""
        CREATE TABLE IF NOT EXISTS regions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        country_id TEXT NOT NULL,
        country_name TEXT NOT NULL,
        region TEXT NOT NULL,
        sub_region TEXT NOT NULL,
        FOREIGN KEY (country_id) REFERENCES iso2_codes(id)
    );
    """)
    cur.execute(query)
    df_to_insert.to_sql('regions', conn, if_exists='append', index=False)
    commit_and_close_db(conn, cur)


def create_table():
    conn, cur = connect_db()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS databank (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date INT,
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

    commit_and_close_db(conn, cur)

def create_and_populate_country_codes():
    conn, cur = connect_db()
    create = ("""
            CREATE TABLE IF NOT EXISTS country_codes (
            id TEXT PRIMARY KEY,
            country TEXT
        );
        """)

    query = ("""
    INSERT INTO country_codes (id, country)
    SELECT i.id, i.country
    FROM iso2_codes i
    WHERE i.id IN (SELECT country_id FROM regions);
    """)

    cur.execute(create)
    cur.execute(query)
    commit_and_close_db(conn, cur)