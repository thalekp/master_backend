from services.parks_list import get_all_parks
from services.constants import price_areas
from src.read_data import read_price
import pandas as pd
import numpy as np

def calc_price_stats():
    all_price_areas = list(set(price_areas().values()))
    spot_data = pd.read_csv(f"aneo_data/spotpris.csv")
    reg_data = pd.read_csv(f"aneo_data/regpris.csv")

    records = []

    for pa in all_price_areas:
        spot_prices = spot_data[spot_data["area"] == pa].value.values
        reg_prices = reg_data[reg_data["area"] == pa].value.values

        record = {
            'price_area': pa,
            'spot_median': np.median(spot_prices),
            'spot_std': np.std(spot_prices),
            'reg_median': np.median(reg_prices),
            'reg_std': np.std(reg_prices)
        }

        records.append(record)

    stats_df = pd.DataFrame(records)
    stats_df.to_csv("files/price_stats.csv", index=False)

calc_price_stats()
