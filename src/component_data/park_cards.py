from services.constants import price_areas
from src.read_data import read_price, read_forecast_data

def generate_park_cards(park_name):
    price_area = price_areas().get(park_name)
    
    spot = list(read_price('spot', price_area)['value'])
    reg = list(read_price('reg', price_area)['value'])
    
    production = read_forecast_data(park_name, json = False)
    
    expected_earning = [spot[i]*production[0][i] for i in range(len(spot))]
    buy_volume = [production[0][i]-production[1][i] for i in range(len(spot))]
    actual_earning = [expected_earning[i]-buy_volume[i]*reg[i] for i in range(len(reg))]

    return {
        'data': [{
            'label': 'expected earning',
            
    }]
    }
    
    
    