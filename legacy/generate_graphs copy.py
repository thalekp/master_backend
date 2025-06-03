from src.read_data import read_forecast_data, read_availability_data, read_price, read_weather_data, read_wind_data
from services.parks_list import get_unprofitable_parks, get_all_parks
from services.constants import price_areas
from src.analysis.extreme_price import find_extreme_prices
from src.analysis.determine_loss_factors import determine_loss_factors
from src.analysis.lower_availability import lower_availability
from src.analysis.explain_volume_imbalance import explain_volume_imbalance
from src.analysis.unforeseen_event import unforeseen_event
from services.constants import price_areas
from src.analysis.determine_status import determine_revenue_grade
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
    red_parks = sorted([p for p in list if p.get('color') == 'error'], key=lambda x: x["imbalance"])
    yellow_parks = sorted([p for p in list if p.get('color') == 'warning'], key=lambda x: x["imbalance"])
    green_parks = sorted([p for p in list if p.get('color') == 'success'], key=lambda x: x["imbalance"])
    
    return red_parks+yellow_parks+green_parks

def get_graph():
    unprofitable_parks = get_unprofitable_parks()
    parks = list(unprofitable_parks.keys())
    all_parks = get_all_parks()
    labels = ["dayahead_reported", "prod"]
    loss_factors = determine_loss_factors()
    all_dayahead_earnings = []
    all_actual_earnings = []
    labels = read_forecast_data(all_parks[0]).get("labels")
        
    for park in all_parks:
            dayahead, prod = read_forecast_data(park, json = False)
            spot = read_price('spot', price_areas().get(park)).value.values.tolist()
            reg = read_price('reg', price_areas().get(park)).value.values.tolist()
            dayahead_earnings = [d*s for d, s in zip(dayahead, spot)]
            all_dayahead_earnings.append(dayahead_earnings)
            actual_earnings = [de-(d-p)*r for de, d, p, r in zip(dayahead_earnings, dayahead, prod, reg)]
            all_actual_earnings.append(actual_earnings)
            
    data =[]
    return_data = []
    if parks: 
        for park in parks:
            exp_str = ""
            price_area = price_areas().get(park)
            factor_data = loss_factors.get(park)
            factors = []
            if factor_data.get('volume_abnormality'):
                exp_str = exp_str+"Big volume imbalance "
                forecast = read_forecast_data(park)
                data.append(forecast)
                less_wind, model_disagreement, availability_reduction, icing = explain_volume_imbalance(park)
                buy_hours_set = set(factor_data.get('buy_hours', []))
                high_price_hours_set = set(factor_data.get('high_price_hours', []))
                overlap_hours = sorted(list(buy_hours_set & high_price_hours_set))
                if overlap_hours:
                    exp_str = exp_str+"coinciding with high prices "
                    availability = read_availability_data(park)
                    price = {
                        "title": f"Pricedata for {price_area}, ({park.capitalize()})",
                        "labels": availability.get("labels"),
                        "datasets": [{"label": "Spotpricee", "color": "info", "data": list(read_price('spot', price_area)['value'].values)}, 
                                    {"label": "Regulationprice", "color": "error", "data":list(read_price('reg', price_area)['value'].values)}],
                        "xAxis": "Time",
                        "yAxis": "€/MWh"
                    }
                    data.append(price)
                if not icing or len(factor_data.get('abnormally_low_production_hours'))>6:
                    if less_wind or model_disagreement:
                        factors.append("differences in weather forecasts ")
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
                        data.append({"title": f"Wind forecasts and measurement {park.replace('aa', 'å').capitalize()}",
                            "labels": labels,
                            "datasets": datasets,
                            "xAxis": "Time",
                            "yAxis": "m/s"})
                    if availability_reduction and len(factor_data.get('abnormally_low_production_hours'))<6:
                        factors.append("lower availability than reported")
                        availability = read_availability_data(park)
                        data.append(availability)
                    if len(factor_data.get('abnormally_low_production_hours'))>2: factors = ['icing']
                else:
                    factors.append("icing")
                exp_str = exp_str+"due to "+list_to_str(factors)
            else:
                availability = read_availability_data(parks[0])
                exp_str = exp_str+"lower availability than reported "
            return_data.append({'park': park, 
                                'title': {'text': f"Imbalance costs for {park.capitalize()}"}, 
                                'subtitle': {'text': exp_str}, 
                                'charts' : data, 
                                'color': determine_revenue_grade(calc_revenue(park), calc_dayahead_revenue(park), park),
                                'imbalance': calc_revenue(park)-calc_dayahead_revenue(park)})
            data = []
        high_volume_imbalance_parks = [p for p, data in loss_factors.items() if data.get('volume_abnormality') and p not in unprofitable_parks]
        for park in high_volume_imbalance_parks:
                exp_str = "Large imbalance volumes "
                factors = []
                forecast = read_forecast_data(park)
                data.append(forecast)
                less_wind, model_disagreement, availability_reduction, icing = explain_volume_imbalance(park)
                if not icing or len(factor_data.get('abnormally_low_production_hours'))<12:
                    if less_wind or model_disagreement:
                        factors.append("deviation in weather forecasts")
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
                        data.append({"title": f"Forecasted and measured wind for {park.replace('aa', 'å').capitalize()}",
                            "labels": labels,
                            "datasets": datasets,
                            "xAxis": "Time",
                            "yAxis": "m/s"})
                    if availability_reduction:
                        factors.append("deviation in availability")
                        availability = read_availability_data(park)
                        data.append(availability)
                    if len(factor_data.get('abnormally_low_production_hours'))>6: factors = ['ising']
                else: 
                    factors = ['ising']
                return_data.append({'park': park, 
                                    'title': {'text': f"Imbalancevolume for {park.capitalize()}"}, 
                                    'subtitle': {'text': exp_str+"because of "+list_to_str(factors)}, 
                                    'charts' : data, 
                                    'color': determine_revenue_grade(calc_revenue(park), calc_dayahead_revenue(park), park),
                                    'imbalance': calc_revenue(park)-calc_dayahead_revenue(park)})
                data = []
    else:
        parks = get_all_parks()
        
        high_volume_imbalance_parks = [park for park, data in loss_factors.items() if data.get('volume_abnormality') and park not in unprofitable_parks]
        for park in high_volume_imbalance_parks:
                forecast = read_forecast_data(park)
                data.append(forecast)
                less_wind, model_disagreement, availability_reduction, icing = explain_volume_imbalance(park)
                if not icing:
                    print("it is true")
                    print(less_wind)
                    print(model_disagreement)
                    if less_wind or model_disagreement:
                        print("yes it is true")
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
                        data.append({"title": f"Forecasted and measured wind for {park.replace('aa', 'å').capitalize()}",
                            "labels": labels,
                            "datasets": datasets,
                            "xAxis": "Klokkeslett",
                            "yAxis": "m/s"})
                    #if availability_reduction:
                    availability = read_availability_data(park)
                    data.append(availability)
                return_data.append({'park': park, 
                                'title': {'text': f"Imbalance costs for {park.capitalize()}"}, 
                                'subtitle': {'text': "High volume imbalance"}, 
                                'charts' : data, 
                                'color': determine_revenue_grade(calc_revenue(park), calc_dayahead_revenue(park), park),
                                'imbalance': calc_revenue(park)-calc_dayahead_revenue(park)})
                data = []
    print("return daya")
    print(return_data)
    sorted_data = sort_parks(return_data)
    print(sorted_data)
               
    return {'data': sorted_data}     