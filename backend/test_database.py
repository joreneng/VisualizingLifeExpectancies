from unittest import TestCase
from backend.database import fetch_data


class Test(TestCase):
    def test_fetch_data(self):
        num_of_entries = 2926
        res = fetch_data("FP.CPI.TOTL.ZG", 2000, 2010)
        assert len(res) == num_of_entries

    def test_populate_data(self):
        res = fetch_data("FP.CPI.TOTL.ZG", 2000, 2002)
