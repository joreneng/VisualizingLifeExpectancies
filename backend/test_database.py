import sqlite3
from unittest import TestCase
from backend.database import fetch_data, process_and_populate_data, add_new_rows_to_table, DB_PATH


class Test(TestCase):
    def test_fetch_data(self):
        num_of_entries = 2926
        res = fetch_data("FP.CPI.TOTL.ZG", 2000, 2010)
        assert len(res) == num_of_entries

    def test_process_and_populate_data(self):
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
