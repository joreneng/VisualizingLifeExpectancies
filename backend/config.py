import os

# Database configuration
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv('DB_PATH')

# API configuration
BASE_URL = "https://api.worldbank.org/v2"
API_FORMAT = "json"

# Data indicators
INDICATORS = {
    "LIFE_EXPECTANCY": "SP.DYN.LE00.IN",
    "HEALTH_EXPENDITURE": "SH.XPD.CHEX.GD.ZS",
    "DEATH_COMM_DISEASES": "SH.DTH.COMM.ZS",
    "DEATH_INJURY": "SH.DTH.INJR.ZS",
    "DEATH_NON_COMM": "SH.DTH.NCOM.ZS",
    "POPULATION": "SP.POP.TOTL"
}

# Time range
START_YEAR = 1960
END_YEAR = 2025
