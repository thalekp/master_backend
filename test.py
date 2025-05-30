import pandas as pd
import numpy as np
from src.read_data import read_forecast_data, read_price
from services.constants import get_date, price_areas
from services.parks_list import get_all_parks
from services.load_stats import load_diff_production_median, load_diff_production_std, load_revenue_diff_median, load_revenue_stdev

target_date = get_date()
all_parks = get_all_parks()
price_area_dict = price_areas()


produced_volumes = []
revenue_differences = {}

for park in all_parks:
    price_area = price_area_dict.get(park)
    dayahead, prod = read_forecast_data(park, target_date, json = False)
    
    spot_price = read_price('spot', price_area, target_date)['value'].values
    reg_price = read_price('reg', price_area, target_date)['value'].values
    
    prod_difference = [p-d for p,d in zip(prod, dayahead)]
    produced_volumes.append(prod_difference)
    
    predicted_revenue = [sp*dh for sp, dh in zip(spot_price, dayahead)]
    imbalance_cost = [rp*(p-d)+pr for rp, p, d, pr in zip(reg_price, prod, dayahead, predicted_revenue)]
    revenue_differences[park] = imbalance_cost

blame_list = [] 
for hour in range(len(revenue_differences.get(all_parks[0]))):
    largest_cost = float('inf')
    cost_blame_park = ""
    total_cost = 0
    for park in all_parks:
        park_revenue = revenue_differences.get(park)[hour]
        if park_revenue < 0: total_cost += park_revenue
        if park_revenue < largest_cost:
            largest_cost = park_revenue
            blame_park = park
            
    if total_cost<0: blame_list.append(f"{int(round(min(largest_cost/total_cost, 1.0), 2)*100)}% av kostnadene pga {blame_park.capitalize()}")
    else: blame_list.append("alle parker i overskudd")




