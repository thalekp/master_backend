from src.read_data import read_forecast_data, csv_to_data, read_availability_data, read_price, read_weather_data
from src.calculations.calc_revenue import calc_revenue
from services.parks_list import get_unprofitable_parks, get_all_parks
from services.constants import price_areas
from src.analysis.extreme_price import find_extreme_prices
from legacy.determine_loss_factors import determine_loss_factors
from src.calculations.calc_dayahead_revenue import calc_dayahead_revenue
import numpy as np

def get_graph():
    unprofitable_parks = get_unprofitable_parks()
    parks = list(unprofitable_parks.keys())
    labels = ["dayahead_reported", "prod"]
    if parks: 
        data = []
        for park in parks:
            timesteps, new_grade, cost =  find_extreme_prices(park)
            revenue = calc_revenue(park)
            dayahead = calc_dayahead_revenue(park)
            blame, no_volume_hours, reg_status, reg_periode, prediction_offset_severity, explanation_weather_sets, replan_improvement, cost, grade = determine_loss_factors(park, revenue+cost, timesteps, dayahead_revenue=dayahead)
            if 'availability' in blame:
                availability = read_availability_data(park)
                data.append(availability)
            if len(timesteps)>0 or 'price' in blame:
                availability = read_availability_data(park)
                
                price = {
                    "title": f"Prisdata for {park}",
                    "labels": availability.get("labels"),
                    "datasets": [{"label": "Spotpris", "color": "dark", "data": list(read_price('spot', price_areas().get(park)).get('value'))}, 
                                {"label": "Reguleringspris", "color": "info", "data":list(read_price('reg', price_areas().get(park)).get('value'))}],
                    "xAxis": "Klokkeslett",
                    "yAxis": "€/MWh"
                }
                data.append(price)
            if new_grade != 'success':
                if no_volume_hours>0 or reg_status>0:
                    forecast = read_forecast_data(park)
                    data.append(forecast)
                if ('availability' in blame or 'volume' in blame) and len(explanation_weather_sets)>0 and not (replan_improvement<0.3 or (replan_improvement < 0.8 and no_volume_hours>5)) and not no_volume_hours>20:

                    weather = read_weather_data(park, services = explanation_weather_sets)
                    for w in weather:
                        data.append(w)
                
        
        return {'data' : data}
    else:
        parks = get_all_parks()
        """all_datasets = [csv_to_data(park, labels, 'park_data', 'series', 'value') for park in parks]
        dayahead_data_list = [all_datasets[i].get("datasets")[0].get("data") for i in range(len(all_datasets))]
        prod_data_list = [all_datasets[i].get("datasets")[1].get("data") for i in range(len(all_datasets))]
        dayahead = [sum([dayahead_data_list[list_idx][internal_idx] for list_idx in range(len(dayahead_data_list))]) for internal_idx in range(len(dayahead_data_list[0]))]
        prod = [sum([prod_data_list[list_idx][internal_idx] for list_idx in range(len(prod_data_list))]) for internal_idx in range(len(prod_data_list[0]))]
        labels = all_datasets[0].get("labels")"""
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
            
        return {'data':[{
            "title": "Inntekt oversikt",
            "labels": labels,
            "datasets": [{"label": "Dayahead inntjening", "color": "dark", "data": np.array(all_dayahead_earnings).sum(axis=0).tolist()}, {"label": "Total inntjening", "color": "info","data": np.array(all_actual_earnings).sum(axis=0).tolist()}],
            "xAxis": "Klokkeslett",
            "yAxis": "Euro overskudd"
        }]}
        