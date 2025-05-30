import pandas as pd
import numpy as np
from src.read_data import read_forecast_data, read_price
from services.constants import get_date, price_areas
from services.parks_list import get_all_parks
from services.load_stats import load_diff_production_median, load_diff_production_std, load_revenue_diff_median, load_revenue_stdev

def get_critical_hours(target_date):
    all_parks = get_all_parks()
    price_area_dict = price_areas()
    produced_volumes = []
    revenue_differences = []

    for park in all_parks:
        price_area = price_area_dict.get(park)
        dayahead, prod = read_forecast_data(park, target_date, json = False)
        
        spot_price = read_price('spot', price_area, target_date)['value'].values
        reg_price = read_price('reg', price_area, target_date)['value'].values
        
        prod_difference = [p-d for p,d in zip(prod, dayahead)]
        produced_volumes.append(prod_difference)
        
        predicted_revenue = [sp*dh for sp, dh in zip(spot_price, dayahead)]
        imbalance_cost = [rp*(p-d)+pr for rp, p, d, pr in zip(reg_price, prod, dayahead, predicted_revenue)]
        revenue_differences.append(imbalance_cost)
        
        

    hourly_revenue = np.sum(revenue_differences, axis=0)

    num_top_losses = 7
    top_loss_indices = np.argsort(hourly_revenue)[:num_top_losses]
    worst_hour = top_loss_indices[0]
    worst_hours = [worst_hour]

    for idx in top_loss_indices[1:]:
        in_sequence = False
        for hour in worst_hours:
            if abs(hour-idx)==1:
                in_sequence = True
        if in_sequence:
            worst_hours.append(idx)
        else:
            break
    
    total_wh_cost = sum([hourly_revenue[i] for i in worst_hours])
    loss_amount = total_wh_cost/sum([i for i in hourly_revenue if i<0])
    
    return sorted(worst_hours), loss_amount


