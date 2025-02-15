import sqlite3
from unittest import TestCase

from backend.queries import keep_only_country_codes, query_table_by_indicator_and_years, \
    query_and_process_wealth_health_values
from db_setup import *
from queries import *

class DatabaseTests(TestCase):
    def test_fetch_data(self):
        num_of_entries = 2926
        res = fetch_data_by_indicator_and_years("FP.CPI.TOTL.ZG", 2000, 2010)
        assert len(res) == num_of_entries

    def test_create_table(self):
        create_table()

    def test_create_and_populate_iso2codes(self):
        create_and_populate_iso2codes()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM iso2_codes")
        row_count = cursor.fetchone()[0]
        self.assertEqual(row_count, 296)
        conn.close()

    def  test_process_and_populate_data(self):
        process_and_populate_data("FP.CPI.TOTL.ZG", 1999, 2002)
        num_of_entries = 1064
        # Additional assertions can be added to verify the data has been populated correctly
        # For example, checking the database for the new entries
        # This part is left as an exercise for the user to implement based on their testing needs

    def test_add_new_rows_to_table(self):
        num_of_entries = 1330
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM databank")
        row_count = cursor.fetchone()[0]
        self.assertEqual(row_count, 1064)

        process_and_populate_data("FP.CPI.TOTL.ZG", 2002, 2003)
        cursor.execute("SELECT COUNT(*) FROM databank")
        row_count = cursor.fetchone()[0]
        self.assertEqual(row_count, num_of_entries)
        conn.close()

    def test_query_and_process_avg_values(self):
        print(query_and_process_avg_values())

    def test_create_and_populate_regions_table(self):
        create_and_populate_regions_table()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM regions")
        row_count = cursor.fetchone()[0]
        assert row_count > 0
        conn.close()

class QueryTests(TestCase):
    def test_query_table(self):
        queried_db = query_table_by_indicator_and_years("FP.CPI.TOTL.ZG", 2002, 2003)
        self.assertEqual(len(queried_db), 532)

    def test_keep_only_country_codes(self):
        keep_only_country_codes()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM country_codes")
        row_count = cursor.fetchone()[0]
        self.assertEqual(row_count, 215)
        conn.close()

    def test_query_and_process_wealth_health_values(self):
        print(query_and_process_wealth_health_values(2000, 2020))

    def test_query_and_process_death_causes(self):
        print(query_and_process_death_causes(2020, 2025))