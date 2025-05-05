from services.parks_list import get_all_parks
from services.constants import price_areas
from src.read_data import read_price
import pandas as pd
import numpy as np
import json

def calc_price_stats():
    all_price_areas = list(set(price_areas().values()))
    spot_data = pd.read_csv(f"aneo_data/spotpris.csv")
    
    reg_data = pd.read_csv(f"aneo_data/regpris.csv")
    
    spot_medians = {}
    reg_medians = {}
    spot_stdevs = {}
    reg_stdevs = {}

    for pa in all_price_areas:

        spot_prices = spot_data[spot_data["area"]==pa].value.values
        spot_median = np.median(spot_prices)
        spot_std = np.std(spot_prices)

        reg_prices = reg_data[reg_data["area"]==pa].value.values
        reg_median = np.median(reg_prices)
        reg_std = np.std(reg_prices)
        
        spot_medians[pa]= spot_median
        reg_medians[pa] = reg_median
        spot_stdevs[pa] = spot_std
        reg_stdevs[pa] = reg_std
    
    with open("files/price_stats.json", "w") as f:
        json.dump({'spot': {'median': spot_medians,
                            'std': spot_stdevs}, 
                   'reg': {'median': reg_medians,
                           'std': reg_stdevs}}, f, indent=2)     
    
calc_price_stats()