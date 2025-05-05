from src.read_data import read_forecast_data, read_availability_data, read_price, read_weather_data, read_wind_data
from services.parks_list import get_unprofitable_parks, get_all_parks
from services.constants import price_areas
from src.analysis.extreme_price import find_extreme_prices
from src.analysis.determine_loss_factors import determine_loss_factors
from src.analysis.lower_availability import lower_availability
from src.analysis.explain_volume_imbalance import explain_volume_imbalance
from src.analysis.unforeseen_event import unforeseen_event
import numpy as np

def get_graph():
    unprofitable_parks = get_unprofitable_parks()
    parks = list(unprofitable_parks.keys())
    labels = ["dayahead_reported", "prod"]
    abnormal_prices, extreme_prices, unforeseen_events, abnormal_volumes, non_extreme_parks = determine_loss_factors()
    print(abnormal_prices, extreme_prices, unforeseen_events, abnormal_volumes, non_extreme_parks)
    if parks: 
        data = []
        for price_area in abnormal_prices+list(extreme_prices.keys()):
            availability = read_availability_data(parks[0])
            price = {
                    "title": f"Prisdata for {price_area}",
                    "labels": availability.get("labels"),
                    "datasets": [{"label": "Spotpris", "color": "dark", "data": list(read_price('spot', price_area)['value'].values)}, 
                                {"label": "Reguleringspris", "color": "info", "data":list(read_price('reg', price_area)['value'].values)}],
                    "xAxis": "Klokkeslett",
                    "yAxis": "€/MWh"
                }
            data.append(price)
        for park in parks:
            timesteps, new_grade, cost =  find_extreme_prices(park)
            if len(lower_availability(park))>0:
                availability = read_availability_data(park)
                data.append(availability)
            if park.capitalize() in non_extreme_parks and park.capitalize() not in abnormal_volumes:
                forecast = read_forecast_data(park)
                data.append(forecast)                 
            if park.capitalize() in abnormal_volumes or park.capitalize() in unforeseen_events:
                less_wind, model_disagreement, availability_reduction, icing = explain_volume_imbalance(park)
                forecast = read_forecast_data(park)
                data.append(forecast)
                if (less_wind or model_disagreement) and len(unforeseen_event(park))<20 and not availability_reduction:
                    weather_data = read_weather_data(park)
                    labels = weather_data[0].get('labels')
                    colors = ['dark', 'primary', 'secondary']
                    datasets = []
                    for weather_service, i in zip(weather_data, range(4)):
                        label = weather_service.get('title')
                        predicted_weather = weather_service.get('datasets')[0].get('data')
                        color = colors[i]
                        datasets.append({"label": label,
                                         "color": color,
                                         "data": predicted_weather})
                    datasets.append({"label": "Målt vind", "color": "info", "data": read_wind_data(park, json = False)[0]})
                    data.append({"title": f"Meldt og målt vind for {park}",
                                "labels": labels,
                                "datasets": datasets,
                                "xAxis": "Klokkeslett",
                                "yAxis": "m/s"})
                if park.capitalize() in non_extreme_parks:
                    availability = read_availability_data(parks[0])
                    price_area = price_areas().get(park)
                    price = {
                            "title": f"Prisdata for {price_area}",
                            "labels": availability.get("labels"),
                            "datasets": [{"label": "Spotpris", "color": "dark", "data": list(read_price('spot', price_area)['value'].values)}, 
                                        {"label": "Reguleringspris", "color": "info", "data":list(read_price('reg', price_area)['value'].values)}],
                            "xAxis": "Klokkeslett",
                            "yAxis": "€/MWh"
                        }
                    data.append(price)
        for park in [p.lower() for p in abnormal_volumes if p.lower() not in unprofitable_parks]:
            less_wind, model_disagreement, availability_reduction, icing = explain_volume_imbalance(park)
            forecast = read_forecast_data(park)
            data.append(forecast)
            if (less_wind or model_disagreement) and len(unforeseen_event(park))<20 and not availability_reduction:
                    weather_data = read_weather_data(park)
                    labels = weather_data[0].get('labels')
                    colors = ['dark', 'primary', 'secondary']
                    datasets = []
                    for weather_service, i in zip(weather_data, range(4)):
                        label = weather_service.get('title')
                        predicted_weather = weather_service.get('datasets')[0].get('data')
                        color = colors[i]
                        datasets.append({"label": label,
                                         "color": color,
                                         "data": predicted_weather})
                    datasets.append({"label": "Målt vind", "color": "info", "data": read_wind_data(park, json = False)[0]})
                    data.append({"title": f"Meldt og målt vind for {park}",
                                "labels": labels,
                                "datasets": datasets,
                                "xAxis": "Klokkeslett",
                                "yAxis": "m/s"})
                
        return {'data' : data}
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
        
        for park in [p.lower() for p in abnormal_volumes]:
            less_wind, model_disagreement, availability_reduction, icing = explain_volume_imbalance(park)
            forecast = read_forecast_data(park)
            data.append(forecast)
            if (less_wind or model_disagreement) and len(unforeseen_event(park))<3 and not availability_reduction:
                    weather_data = read_weather_data(park)
                    labels = weather_data[0].get('labels')
                    colors = ['dark', 'primary', 'secondary']
                    datasets = []
                    for weather_service, i in zip(weather_data, range(4)):
                        label = weather_service.get('title')
                        predicted_weather = weather_service.get('datasets')[0].get('data')
                        color = colors[i]
                        datasets.append({"label": label,
                                         "color": color,
                                         "data": predicted_weather})
                    datasets.append({"label": "Målt vind", "color": "info", "data": read_wind_data(park, json = False)[0]})
                    data.append({"title": f"Meldt og målt vind for {park}",
                                "labels": labels,
                                "datasets": datasets,
                                "xAxis": "Klokkeslett",
                                "yAxis": "m/s"})
                
        return {'data' : data}        