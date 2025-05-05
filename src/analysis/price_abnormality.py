from src.read_data import read_forecast_data, read_price
from services.constants import price_areas
from services.load_stats import load_diff_production_median, load_diff_production_std, load_reg_median, load_reg_std


def price_abnormality(price_area, target_day=None):
    reg_median = load_reg_median(price_area)
    reg_std = load_reg_std(price_area)
    reg_price = read_price('reg', price_area, target_day)['value'].values.tolist()
    z_reg_price = [(r-reg_median)/reg_std for r in reg_price]
    max_price_extremity = max(z_reg_price)
    high_prices = [i for z, i in zip(z_reg_price, range(24)) if abs(z)>1]
    return max_price_extremity, high_prices