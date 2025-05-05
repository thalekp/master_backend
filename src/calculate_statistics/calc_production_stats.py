import pandas as pd
from src.calculations.calc_revenue import calc_revenue
from src.calculations.calc_dayahead_revenue import calc_dayahead_revenue
from src.read_data import read_forecast_data
from services.parks_list import get_all_parks
import numpy as np

def store_park_production_stats():
    parks = get_all_parks()

    records = []

    for park in parks:
        df = pd.read_csv(f"aneo_data/{park.replace('aa', 'å')}_park_data.csv")
        df["time"] = pd.to_datetime(df["time"])
        df["date"] = df["time"].dt.date
        df["time"] = df["time"].dt.strftime("%H:%M")

        dates = sorted(set(df["date"]))[:-2]  # exclude last two days for stability

        dayahead_list = []
        prod_list = []
        diff_list = []

        for date in dates:
            dayahead, prod = read_forecast_data(park, target_day=date, json=False)
            diff = [produced - predicted for produced, predicted in zip(prod, dayahead)]
            dayahead_list.append(sum(dayahead))
            prod_list.append(sum(prod))
            diff_list.append(sum(diff))

        record = {
            "park": park,
            "dayahead_median": np.median(dayahead_list),
            "prod_median": np.median(prod_list),
            "diff_median": np.median(diff_list),
            "dayahead_std": np.std(dayahead_list),
            "prod_std": np.std(prod_list),
            "diff_std": np.std(diff_list),
        }

        records.append(record)

    stats_df = pd.DataFrame(records)
    stats_df.to_csv("files/production_stats.csv", index=False)

store_park_production_stats()
