from src.read_data import read_forecast_data, read_wind_data, read_weather_data
from src.analysis.lower_availability import lower_availability

import numpy as np


def explain_volume_imbalance(park):

    park_name = park.lower()
    dayahead, prod = read_forecast_data(park_name, json = False)
    weather = [d for d, r in read_weather_data(park_name, json = False)]
    actual_wind = read_wind_data(park_name, json = False)
    availability_drop = lower_availability(park_name)
    
    forecast_wind_avg = np.mean(weather, axis=0) 
    wind_diff = np.array(actual_wind) - forecast_wind_avg
    avg_wind_diff = np.mean(wind_diff)
    max_model_spread = np.max(np.ptp(weather, axis=0))
    
    hours_lower_wind = len([i for i, wind in zip(range(24), wind_diff[0]) if wind<0])
    hours_under_production = len([i for i, d, p in zip(range(24), dayahead, prod) if p<d])

    
    if avg_wind_diff < -1.5 and hours_under_production>=hours_lower_wind*0.5:
        less_wind = True
    else:
        less_wind = False

    if max_model_spread > 2:
        model_disagreement = True
    else:
        model_disagreement = False


    if len(availability_drop)>0:
        availability_reduction = True
    else:
        availability_reduction = False

    if np.mean(actual_wind) > 3 and np.mean(prod) < 0.5 * np.mean(dayahead):
        icing = True
    else:
        icing = False

    
    return less_wind, model_disagreement, availability_reduction, icing