import pandas as pd
from src.read_data import read_forecast_data, read_price, read_availability_data, read_weather_data
from services.constants import price_areas

def park_report(park_name, target_day = None):
    forecast = read_forecast_data(park_name)
    
    availability = read_availability_data(park_name)
    
    
    weather = read_weather_data(park_name)
    
    price = {
            "title": f"Prisdata for {park_name}",
            "labels": availability.get("labels"),
            "datasets": [{"label": "Spotpris", "color": "dark", "data": list(read_price('spot', price_areas().get(park_name)).get('value'))}, 
                         {"label": "Reguleringspris", "color": "info", "data":list(read_price('reg', price_areas().get(park_name)).get('value'))}],
            "xAxis": "klokkeslett",
            "yAxis": "Euro per MWh"
        }
    return{
        "label": f"Park report for {park_name} {target_day}",
        "datasets": [price, forecast, availability, *weather]
    }