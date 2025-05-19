from services.parks_list import get_unprofitable_parks, get_all_parks
from src.calculations.calc_revenue import calc_revenue
from src.calculations.calc_dayahead_revenue import calc_dayahead_revenue
from src.analysis.price_abnormality import price_abnormality
from src.analysis.volume_abnormality import volume_abnormality
from services.constants import price_areas_list, get_price_area_parks, price_areas
from src.analysis.extreme_prices import find_extreme_prices
from src.analysis.unforeseen_event import unforeseen_event
from src.analysis.lower_availability import lower_availability

def determine_loss_factors():
    unprofitable_parks = get_unprofitable_parks()
    all_parks = get_all_parks()
    explained_parks = []
    extreme_prices = {}
    
    
    non_extreme_prices = []
    abnormal_volumes = []
    unforeseen_events = []
    
    output_dict = {}
    for pa in price_areas_list():
        connected_parks = get_price_area_parks(pa)
        relevant_parks = len([p for p in connected_parks if p in unprofitable_parks])
        if price_abnormality(pa)[0]>1 and relevant_parks>0: 
            for park in get_price_area_parks(pa):
                explained_parks.append(park)
            timesteps = find_extreme_prices(pa)
            if len(timesteps)>0:
                extreme_prices[pa] = timesteps
            else: 
                non_extreme_prices.append(pa)
                

    for p in all_parks:
        if p in unprofitable_parks: unprofitable = True
        else: unprofitable = False
        abnormal_volume = False
        abnormal_timesteps = unforeseen_event(p)
        price_area = price_areas().get(p.lower())
        
        if len(abnormal_timesteps)>3 and p in unprofitable_parks: 
            unforeseen_events.append(p.capitalize())
        volume_abnormality_score, buy_hours, sell_hours = volume_abnormality(p)
        if volume_abnormality_score<-1: 
            abnormal_volume = True
            explained_parks.append(p)
            if p in unprofitable_parks:
                abnormal_volumes.insert(0, p.capitalize())
            else: 
                abnormal_volumes.append(p.capitalize())
                
        if p and not p in explained_parks:
            if not abs(volume_abnormality_score)>abs(price_abnormality(price_area)[0]):
                non_extreme_prices.append(price_area)             
        price_status = 'normal'
        high_price_hours = []
        if price_area in non_extreme_prices: 
            price_status = 'high'
            high_price_hours = price_abnormality(price_area)[1]
        if price_area in extreme_prices.keys():
            price_status = 'extreme'
            high_price_hours = extreme_prices.get(price_area)
        park_explanation = {
                'unprofitable': unprofitable,
                'abnormally_low_production_hours': abnormal_timesteps,
                'volume_abnormality': abnormal_volume,
                'price_status' : price_status,
                'high_price_hours': high_price_hours,
                'buy_hours': buy_hours,
                'sell_hours': sell_hours
        }
        output_dict[p] = park_explanation
    
    return output_dict
    #return output_dict, non_extreme_prices, extreme_prices, unforeseen_events, abnormal_volumes, non_extreme_parks
