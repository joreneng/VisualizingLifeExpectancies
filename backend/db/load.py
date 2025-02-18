from backend.db.setup import process_and_populate_data
from backend.config import INDICATORS

def load_db():
    # Life expectancy at birth, total (years)
    process_and_populate_data(INDICATORS["LIFE_EXPECTANCY"], 1960, 2025)

    # Current health expenditure (% of GDP)
    process_and_populate_data(INDICATORS["HEALTH_EXPENDITURE"], 1960, 2025)

    # # Cause of death, by communicable diseases and maternal,
    # # prenatal and nutrition conditions (% of total)
    process_and_populate_data(INDICATORS["DEATH_COMM_DISEASES"], 2000, 2025)

    # Cause of death, by injury (% of total)
    process_and_populate_data(INDICATORS["DEATH_INJURY"], 2000, 2025)

    # Cause of death, by non-communicable diseases (% of total)
    process_and_populate_data(INDICATORS["DEATH_NON_COMM"], 2000, 2025)

    # Population, total
    process_and_populate_data(INDICATORS["POPULATION"], 1960, 2025)
