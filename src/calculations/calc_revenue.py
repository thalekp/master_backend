from src.read_data import read_forecast_data, read_price
from services.constants import get_date, price_areas
from src.analysis.park_imbalance_lists import actual_earning

def calc_revenue(parkname, target_date=None):
    if not target_date: target_date = get_date()
    result = actual_earning(parkname, target_date)
    return sum(result)