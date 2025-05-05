from src.read_data import read_forecast_data, read_price
from services.constants import price_areas
from services.load_stats import load_reg_median, load_reg_std
from services.config import extreme_price_threshold

def find_extreme_prices(price_area, target_day = None):
    reg_price = list(read_price('reg', price_area, target_day)['value'])
    threshold = extreme_price_threshold.get(price_area)
    
    #Extreme reg price
    median_reg = load_reg_median(price_area)
    std_reg = load_reg_std(price_area)
    extreme_reg = [i for i,r in enumerate(reg_price) if abs(r-median_reg)>threshold*std_reg]

    return extreme_reg