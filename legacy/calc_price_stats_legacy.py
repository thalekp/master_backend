from services.parks_list import get_all_parks
from services.constants import price_areas
from src.read_data import read_price
import pandas as pd
import numpy as np
import json

def calc_price_stats():
    all_price_areas = list(set(price_areas().values()))
    df = pd.read_csv(f"aneo_data/spotpris.csv")
    df["time"] =  pd.to_datetime(df["time"])
    df["date"] = df["time"].dt.date
    df["time"] = df["time"].dt.strftime("%H:%M")
    
    dates = list(set(df["date"].copy()))
    dates.sort()
    dates = dates[:-2]
    
    spot_medians = {}
    reg_medians = {}
    spot_stdevs = {}
    reg_stdevs = {}

    for pa in all_price_areas:
        spot_prices = []
        reg_prices = []
        for date in dates:
            spot_price = list(read_price('spot', pa, date)['value'])
            reg_price = list(read_price('reg', pa, date)['value'])
            spot_prices.append(spot_price)
            reg_prices.append(reg_price)
        spot_median = list(np.median(np.array(spot_prices), axis = 0))  
        reg_median = list(np.median(np.array(reg_prices), axis = 0))
        spot_stdev = list(np.std(np.array(spot_prices), axis = 0))
        reg_stdev = list(np.std(np.array(reg_prices), axis = 0))
        spot_medians[pa] = spot_median
        reg_medians[pa] = reg_median
        spot_stdevs[pa] = spot_stdev
        reg_stdevs[pa] = reg_stdev
    
    with open("files/price_medians.json", "w") as f:
        json.dump({'spot': {'median': spot_medians,
                            'std': spot_stdevs}, 
                   'reg': {'median': reg_medians,
                           'std': reg_stdevs}}, f, indent=2)     
    
calc_price_stats()