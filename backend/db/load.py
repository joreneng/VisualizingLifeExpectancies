from backend.config import INDICATORS
from backend.db.setup import process_and_populate_data
from backend.utils import create_and_populate_iso2codes, create_and_populate_regions, create_table, \
    create_and_populate_country_codes


def load_db():
    # Create databank table in db
    create_table()

    # Create static db tables
    create_and_populate_iso2codes()
    create_and_populate_regions()
    create_and_populate_country_codes()

    # Life expectancy at birth, total (years)
    process_and_populate_data(INDICATORS["LIFE_EXPECTANCY"], 1960, 2025)

    # Current health expenditure (% of GDP)
    process_and_populate_data(INDICATORS["HEALTH_EXPENDITURE"], 1960, 2025)

    # Cause of death, by communicable diseases and maternal,
    # prenatal and nutrition conditions (% of total)
    process_and_populate_data(INDICATORS["DEATH_COMM_DISEASES"], 2000, 2025)

    # Cause of death, by injury (% of total)
    process_and_populate_data(INDICATORS["DEATH_INJURY"], 2000, 2025)

    # Cause of death, by non-communicable diseases (% of total)
    process_and_populate_data(INDICATORS["DEATH_NON_COMM"], 2000, 2025)

    # Population, total
    process_and_populate_data(INDICATORS["POPULATION"], 1960, 2025)
