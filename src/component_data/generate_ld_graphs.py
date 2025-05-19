from src.read_data import read_forecast_data, read_availability_data, read_price, read_weather_data, read_wind_data
from services.parks_list import get_unprofitable_parks, get_all_parks
from services.constants import price_areas
from src.analysis.extreme_price import find_extreme_prices
from src.analysis.determine_loss_factors import determine_loss_factors
from src.analysis.lower_availability import lower_availability
from src.analysis.explain_volume_imbalance import explain_volume_imbalance
from src.analysis.unforeseen_event import unforeseen_event
from services.constants import price_areas
import numpy as np

def get_ld_graph():
    unprofitable_parks = get_unprofitable_parks()
    parks = list(unprofitable_parks.keys())
    labels = ["dayahead_reported", "prod"]
    loss_factors = determine_loss_factors()
    data = []
    if parks: 
        for park in parks:
            price_area = price_areas().get(park)
            factor_data = loss_factors.get(park)
            if factor_data.get('volume_abnormality'):
                forecast = read_forecast_data(park)
                data.append(forecast)
                less_wind, model_disagreement, availability_reduction, icing = explain_volume_imbalance(park)
                buy_hours_set = set(factor_data.get('buy_hours', []))
                high_price_hours_set = set(factor_data.get('high_price_hours', []))
                overlap_hours = sorted(list(buy_hours_set & high_price_hours_set))
                if overlap_hours:
                    availability = read_availability_data(parks[0])
                    price = {
                        "title": f"Prisdata for {price_area}, ({park.capitalize()})",
                        "labels": availability.get("labels"),
                        "datasets": [{"label": "Spotpris", "color": "dark", "data": list(read_price('spot', price_area)['value'].values)}, 
                                    {"label": "Reguleringspris", "color": "info", "data":list(read_price('reg', price_area)['value'].values)}],
                        "xAxis": "Klokkeslett",
                        "yAxis": "€/MWh"
                    }
                    data.append(price)
            else:
                availability = read_availability_data(parks[0])
                price = {
                        "title": f"Prisdata for {price_area}, ({park.capitalize()})",
                        "labels": availability.get("labels"),
                        "datasets": [{"label": "Spotpris", "color": "dark", "data": list(read_price('spot', price_area)['value'].values)}, 
                                    {"label": "Reguleringspris", "color": "info", "data":list(read_price('reg', price_area)['value'].values)}],
                        "xAxis": "Klokkeslett",
                        "yAxis": "€/MWh"
                    }
                data.append(price)
        high_volume_imbalance_parks = [park for park, data in loss_factors.items() if data.get('volume_abnormality') and park not in unprofitable_parks]
        for park in high_volume_imbalance_parks:
                forecast = read_forecast_data(park)
                data.append(forecast)
                less_wind, model_disagreement, availability_reduction, icing = explain_volume_imbalance(park)
    else:
        parks = get_all_parks()
        all_dayahead_earnings = []
        all_actual_earnings = []
        labels = read_forecast_data(parks[0]).get("labels")
        
        for park in parks:
            dayahead, prod = read_forecast_data(park, json = False)
            spot = read_price('spot', price_areas().get(park)).value.values.tolist()
            reg = read_price('reg', price_areas().get(park)).value.values.tolist()
            dayahead_earnings = [d*s for d, s in zip(dayahead, spot)]
            all_dayahead_earnings.append(dayahead_earnings)
            actual_earnings = [de-(d-p)*r for de, d, p, r in zip(dayahead_earnings, dayahead, prod, reg)]
            all_actual_earnings.append(actual_earnings)
            
        data =[{
            "title": "Inntekt oversikt",
            "labels": labels,
            "datasets": [{"label": "Dayahead inntjening", "color": "dark", "data": np.array(all_dayahead_earnings).sum(axis=0).tolist()}, {"label": "Total inntjening", "color": "info","data": np.array(all_actual_earnings).sum(axis=0).tolist()}],
            "xAxis": "Klokkeslett",
            "yAxis": "Euro overskudd"
        }]
        
        high_volume_imbalance_parks = [park for park, data in loss_factors.items() if data.get('volume_abnormality') and park not in unprofitable_parks]
        for park in high_volume_imbalance_parks:
                forecast = read_forecast_data(park)
                data.append(forecast)
                
    return {'data' : data}        