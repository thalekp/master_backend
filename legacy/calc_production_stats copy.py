import pandas as pd
from src.calculations.calc_revenue import calc_revenue
from src.calculations.calc_dayahead_revenue import calc_dayahead_revenue
from src.read_data import read_forecast_data
from services.parks_list import get_all_parks
import json
import numpy as np

def store_park_production_stats():

    parks = get_all_parks()

    dayahead_medians = {}
    prod_medians = {}
    diff_medians = {}
    dayahead_stds = {}
    prod_stds = {}
    diff_stds = {}
    
    
    for park in parks:
        df = pd.read_csv(f"aneo_data/{park.replace('aa', 'å')}_park_data.csv")
        df["time"] =  pd.to_datetime(df["time"])
        df["date"] = df["time"].dt.date
        df["time"] = df["time"].dt.strftime("%H:%M")
        
        dates = list(set(df["date"].copy()))
        dates.sort()
        dates = dates[:-2]
        
        dayahead_list = []
        prod_list = []
        diff_list = []
        
        for date in dates:
            dayahead, prod = read_forecast_data(park, target_day=date, json = False)
            diff = [produced-predicted for produced, predicted in zip(prod, dayahead)]
            dayahead_list.append(sum(dayahead))
            prod_list.append(sum(prod))
            diff_list.append(sum(diff))
            
        dayahead_median = np.median(dayahead_list) 
        prod_median = np.median(prod_list)
        diff_median = np.median(diff_list)
        dayahead_std = np.std(dayahead_list) 
        prod_std = np.std(prod_list) 
        diff_std = np.std(diff_list) 
        
        dayahead_medians[park] = dayahead_median
        prod_medians[park] = prod_median
        diff_medians[park] = diff_median
        dayahead_stds[park] = dayahead_std
        prod_stds[park] = prod_std
        diff_stds[park] = diff_std
    
    with open("files/production_stats.json", "w") as f:
        json.dump({
            'dayahead': {
                'median': dayahead_medians,
                'std': dayahead_stds
            },
            'prod': {
                'median': prod_medians,
                'std': prod_stds
            },
            'diff': {
                'median': diff_medians,
                'std': diff_stds
            }
        }, f, indent=2)
        
            
        
        
store_park_production_stats()