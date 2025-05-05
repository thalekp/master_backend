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
    for pa in price_areas_list():
        connected_parks = get_price_area_parks(pa)
        relevant_parks = len([p for p in connected_parks if p in unprofitable_parks])
        if price_abnormality(pa)>1 and relevant_parks>0: 
            for park in get_price_area_parks(pa):
                explained_parks.append(park)
            timesteps = find_extreme_prices(pa)
            if len(timesteps)>0:
                extreme_prices[pa] = timesteps
            else: 
                non_extreme_prices.append(pa)
    for p in all_parks:
        abnormal_timesteps = unforeseen_event(p)
        if len(abnormal_timesteps)>3 and p in unprofitable_parks: 
            unforeseen_events.append(p.capitalize())
        if volume_abnormality(p)<-1: 
            explained_parks.append(p)
            if p in unprofitable_parks: abnormal_volumes.insert(0, p.capitalize())
            else: abnormal_volumes.append(p.capitalize())
    non_extreme_parks = [p.capitalize() for p in unprofitable_parks if p not in explained_parks]
    for park in non_extreme_parks:
        price_area = price_areas().get(park.lower())
        if abs(volume_abnormality(park.lower()))>abs(price_abnormality(price_area)):
            abnormal_volumes.insert(0, park.capitalize())
        else:
            non_extreme_prices.append(price_area)
    return non_extreme_prices, extreme_prices, unforeseen_events, abnormal_volumes, non_extreme_parks
