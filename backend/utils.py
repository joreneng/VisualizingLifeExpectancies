import pandas as pd
import requests

from backend.db.setup import connect_db, commit_and_close_db

# Helper to remove non-country codes from iso2_codes before I discovered a regions database online
def keep_only_country_codes():
    country_ids_to_delete = ['EU', 'OE', 'XC', 'XD', 'XE', 'XF', 'XG', 'XH', 'XI',
                             'XJ', 'XL', 'XM', 'XN', 'XO', 'XP', 'XQ', 'XT', 'XU', 'PS'
                             'XY', 'ZB', 'ZF', 'ZG', 'ZH', 'ZI', 'ZJ', 'ZQ', 'ZT']
    country_ids_str = ', '.join(f"'{country_id}'" for country_id in country_ids_to_delete)

    conn, cur = connect_db()
    delete_query = f"""
    DELETE FROM country_codes
    WHERE id IN ({country_ids_str})
    OR id GLOB '*[0-9]*';
    """
    cur.execute(delete_query)
    commit_and_close_db(conn, cur)


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


def create_and_populate_regions_table():
    df = pd.read_json('../../data/countries_with_region.json')
    df.rename(columns={'alpha-2': 'country_id',
                       'name': 'country_name', 'sub-region': 'sub_region'}, inplace=True)
    cols = ['country_id', 'country_name', 'region', 'sub_region']
    df_to_insert = df[cols]
    df_to_insert = df_to_insert.dropna(subset=['country_id', 'country_name', 'region', 'sub_region'])

    conn, cur = connect_db()
    query = ("""
        CREATE TABLE regions (
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
