from src.read_data import read_forecast_data, read_availability_data, read_price, read_weather_data, read_wind_data, read_intraday_volumes
from services.parks_list import get_unprofitable_parks, get_all_parks
from services.constants import price_areas
from src.analysis.extreme_price import find_extreme_prices
from src.analysis.determine_loss_factors import determine_loss_factors
from src.analysis.lower_availability import lower_availability
from src.analysis.explain_volume_imbalance import explain_volume_imbalance
from src.analysis.unforeseen_event import unforeseen_event
from services.constants import price_areas
from src.analysis.determine_status import determine_revenue_grade, determine_volume_grade
from src.calculations.calc_dayahead_revenue import calc_dayahead_revenue
from src.calculations.calc_revenue import calc_revenue

def list_to_str(list):
    if len(list)==0:
        return ""
    elif len(list)==1:
        return list[0]
    else:
        return_str = list[0]
        for index in range(len(list[1:])):
            if index == len(list)-2:
                return_str = return_str+" and "+list[index+1]
            else:
                return_str = return_str+", "+list[index+1]
        return return_str
    
def sort_parks(list):
    red_parks = sorted([p for p in list if p.get('data')[0].get('color') == 'error'], key=lambda x: x["imbalance"])
    yellow_parks = sorted([p for p in list if p.get('data')[0].get('color') == 'warning'], key=lambda x: x["imbalance"])
    green_parks = sorted([p for p in list if p.get('data')[0].get('color') == 'success'], key=lambda x: x["imbalance"])
    
    return red_parks+yellow_parks+green_parks

def determine_main_cause(factors, unusual_hours):
    less_wind, model_disagreement, availability_reduction, icing = factors
    if len(unusual_hours)>2:
        return 'icing'
    if less_wind or model_disagreement:
        return 'wind forecast deviation'
    if availability_reduction:
        return 'availability'
    else:
        return 'mystery'
    

def get_graph():
    
    all_parks = get_all_parks()
    print(all_parks)
    loss_factors = determine_loss_factors()
    volume_causes = {}
    
    return_data = []
    
    for park in all_parks:
        factor_data = loss_factors.get(park)
        if factor_data.get('volume_abnormality'):
            main_cause = determine_main_cause(explain_volume_imbalance(park), factor_data.get('abnormally_low_production_hours'))
            if main_cause != 'mystery':
                volume_causes [park] = main_cause
            else: 
                volume_causes [park] = 'wind forecast deviation'
        else: 
            volume_causes [park] = 'wind forecast deviation'
    
    print(volume_causes)
    volume_data = {}
    for park in all_parks:
        park_volume_data = {}
        
        #Forecast Data
        forecast = read_forecast_data(park)
        park_volume_data['forecasts'] = forecast
        
        #Availability Data
        availability = read_availability_data(park)
        park_volume_data['availability'] = availability
        
        #Weather Data
        weather_data = read_weather_data(park)
        labels = weather_data[0].get('labels')
        colors = ['dark', 'secondary', 'light']
        datasets = []
        for weather_service, i in zip(weather_data, range(4)):
                            label = weather_service.get('title')
                            predicted_weather = weather_service.get('datasets')[0].get('data')
                            color = colors[i]
                            datasets.append({"label": label,
                                            "color": color,
                                            "data": predicted_weather})
        datasets.append({"label": "Measured wind", "color": "primary", "data": read_wind_data(park, json = False)[0]})
        park_volume_data['weather_data'] = {"title": f"Wind forecasts and measurement {park.replace('aa', 'å').capitalize()}",
                            "labels": labels,
                            "datasets": datasets,
                            "xAxis": "Time",
                            "yAxis": "m/s"}
        volume_data[park] = park_volume_data
    
    market_data = {}
    for park in all_parks:
        park_market_data = {}
        price_area = price_areas().get(park)
        
        #Spot and Regprice
        price = {
                        "title": f"Imbalancepricedata for {price_area}",
                        "labels": availability.get("labels"),
                        "datasets": [{"label": "Spotprice", "color": "info", "data": list(read_price('spot', price_area)['value'].values)}, 
                                    {"label": "Regulationprice", "color": "error", "data":list(read_price('reg', price_area)['value'].values)}],
                        "xAxis": "Time",
                        "yAxis": "€/MWh"
                    }
        park_market_data['imbalancecost'] = price
        
        #Intraday volumes
        intraday_volumes = read_intraday_volumes(price_area)
        park_market_data['intraday_volumes'] = intraday_volumes
        
        #Intraday_prices
        intraday_prices = {
                        "title": f"Intraday pricedata for {price_area}",
                        "labels": availability.get("labels"),
                        "datasets": [{"label": "Sell price intraday", "color": "info", "data": list(read_price('intraday_VWAP_sell', price_area).values)}, 
                                    {"label": "Buy price intraday", "color": "error", "data":list(read_price('intraday_VWAP_buy', price_area).values)}],
                        "xAxis": "Time",
                        "yAxis": "€/MWh"
                    }
        park_market_data['intraday_prices'] = intraday_prices
        
        market_data[park] = park_market_data
    
    
    relevant_charts = {'icing': ['forecasts', 'availability', 'weather_data'],
                        'wind forecast deviation': ['forecasts', 'weather_data'],
                        'availability': ['forecasts', 'availability']}
    for park in all_parks:
        park_overview = {'park': park,
         'imbalance': calc_revenue(park)-calc_dayahead_revenue(park),
         'data': []}
        if park in volume_causes.keys():
            park_overview['data'] = park_overview.get('data') + [{
                                    'title': {'text': f"Imbalance costs for {park.capitalize()}"}, 
                                    'subtitle': {'text': f"High volume imbalance due to {volume_causes.get(park)}"}, 
                                    'charts' : [volume_data.get(park).get(k) for k in volume_data.get(park).keys() if k in relevant_charts.get(volume_causes.get(park))], 
                                    'color': determine_volume_grade(sum(volume_data.get(park).get('forecasts').get('datasets')[1].get('data')), sum(volume_data.get(park).get('forecasts').get('datasets')[0].get('data')), park)
                                    }]
            if len([volume_data.get(park).get(k) for k in volume_data.get(park).keys() if k not in relevant_charts.get(volume_causes.get(park))])>0:
                park_overview['data'] = park_overview.get('data') + [{
                                            'title': {'text': f"Park Data for {park.capitalize()}"}, 
                                            'subtitle': {'text': ""}, 
                                            'charts' : [volume_data.get(park).get(k) for k in volume_data.get(park).keys() if k not in relevant_charts.get(volume_causes.get(park))], 
                                            'color': None
                                            }]
        else:
            park_overview['data'] = park_overview.get('data') + [{
                                            'title': {'text': f"Park Data for {park.capitalize()}"}, 
                                            'subtitle': {'text': ""}, 
                                            'charts' : [volume_data.get(park).get(k) for k in volume_data.get(park).keys()], 
                                            'color': None
                                            }]
        park_overview['data'] = park_overview.get('data') + [{
                                        'title': {'text': f"Market Data for {park.capitalize()}"}, 
                                        'subtitle': {'text': ""}, 
                                        'charts' : [market_data.get(park).get(k) for k in market_data.get(park).keys()], 
                                        'color': determine_revenue_grade(calc_revenue(park), calc_dayahead_revenue(park), park)
                                        }]
        return_data.append(park_overview)     
    
 
    return {'data': return_data}

get_graph()