from unittest import TestCase
from backend.utils import keep_only_country_codes, create_and_populate_iso2codes, create_and_populate_regions_table
from backend.db.setup import *
from backend.db.fetch import *

class DatabaseTests(TestCase):
    def test_fetch_data(self):
        num_of_entries = 2926
        res = fetch_data_by_indicator_and_years("FP.CPI.TOTL.ZG", 2000, 2010)
        assert len(res) == num_of_entries

    def test_create_table(self):
        create_table()

    def test_create_and_populate_iso2codes(self):
        create_and_populate_iso2codes()
        conn, cur = connect_db()
        cur.execute("SELECT COUNT(*) FROM iso2_codes")
        row_count = cur.fetchone()[0]
        self.assertEqual(row_count, 296)
        cur.close()
        conn.close()

    def test_process_and_populate_data(self):
        process_and_populate_data("FP.CPI.TOTL.ZG", 1999, 2002)
        conn, cur = connect_db()
        cur.execute("SELECT COUNT(*) FROM databank")
        row_count = cur.fetchone()[0]
        self.assertEqual(row_count, 1064)
        cur.close()
        conn.close()

    def test_add_new_rows_to_table(self):
        num_of_entries = 1330
        conn, cur = connect_db()

        cur.execute("SELECT COUNT(*) FROM databank")
        row_count = cur.fetchone()[0]
        self.assertEqual(row_count, 1064)

        process_and_populate_data("FP.CPI.TOTL.ZG", 2002, 2003)
        cur.execute("SELECT COUNT(*) FROM databank")
        row_count = cur.fetchone()[0]
        self.assertEqual(row_count, num_of_entries)
        cur.close()
        conn.close()

    def test_query_and_process_avg_values(self):
        result = query_and_process_avg_values()
        self.assertIsInstance(result, dict)

    def test_create_and_populate_regions_table(self):
        create_and_populate_regions_table()
        conn, cur = connect_db()
        cur.execute("SELECT COUNT(*) FROM regions")
        row_count = cur.fetchone()[0]
        self.assertGreater(row_count, 0)
        cur.close()
        conn.close()

class QueryTests(TestCase):
    def test_keep_only_country_codes(self):
        keep_only_country_codes()
        conn, cur = connect_db()
        cur.execute("SELECT COUNT(*) FROM country_codes")
        row_count = cur.fetchone()[0]
        self.assertEqual(row_count, 215)
        cur.close()
        conn.close()

    def test_query_and_process_wealth_health_values(self):
        result = query_and_process_wealth_health_values(2000, 2020)
        self.assertIsInstance(result, dict)

    def test_query_and_process_death_causes(self):
        result = query_and_process_death_causes(2020, 2025)
        self.assertIsInstance(result, list)

    def test_find_life_expectancy_of_countries_by_years(self):
        result = find_life_expectancy_of_countries_by_years(1960, 2025)
        result = query_and_process_life_expectancies(1960, 2025)
        self.assertIsInstance(result, list)