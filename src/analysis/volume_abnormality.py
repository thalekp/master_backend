from src.read_data import read_forecast_data, read_price
from services.constants import price_areas
from services.load_stats import load_diff_production_median, load_diff_production_std, load_reg_median, load_reg_std

def volume_abnormality(park_name, target_date = None):
        print(park_name)
        dayahead_production, produced_production = read_forecast_data(park_name, target_date, json = False)
        expected_production_volume = sum(dayahead_production)
        actual_production_volume = sum(produced_production)
        imbalance_volume = actual_production_volume-expected_production_volume
        median_imbalance_volume = load_diff_production_median(park_name)
        std_imbalance_volume = load_diff_production_std(park_name)
        volume_abnormality = ((imbalance_volume-median_imbalance_volume)/std_imbalance_volume)
        return volume_abnormality
        