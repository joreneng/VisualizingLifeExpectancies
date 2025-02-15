from backend.db_setup import process_and_populate_data

LIFE_EXPECTANCY_SERIES = 'SP.DYN.LE00.IN'
HEALTH_EXPENDITURE_SERIES = 'SH.XPD.CHEX.GD.ZS'
DEATH_BY_COMM_DISEASES_SERIES = 'SH.DTH.COMM.ZS'
DEATH_BY_INJURY_SERIES = 'SH.DTH.INJR.ZS'
DEATH_BY_NON_COMM_DISEASES_SERIES = 'SH.DTH.NCOM.ZS'
POPULATION_TOTAL_SERIES = 'SP.POP.TOTL'

def load_db():
    # Life expectancy at birth, total (years)
    process_and_populate_data(LIFE_EXPECTANCY_SERIES, 1960, 2025)

    # Current health expenditure (% of GDP)
    process_and_populate_data(HEALTH_EXPENDITURE_SERIES, 1960, 2025)

    # # Cause of death, by communicable diseases and maternal,
    # # prenatal and nutrition conditions (% of total)
    process_and_populate_data(DEATH_BY_COMM_DISEASES_SERIES, 2000, 2025)

    # Cause of death, by injury (% of total)
    process_and_populate_data(DEATH_BY_INJURY_SERIES, 2000, 2025)

    # Cause of death, by non-communicable diseases (% of total)
    process_and_populate_data(DEATH_BY_NON_COMM_DISEASES_SERIES, 2000, 2025)

    # Population, total
    process_and_populate_data(POPULATION_TOTAL_SERIES, 1960, 2025)
