from services.parks_list import get_all_parks
from src.calculations.calc_revenue import calc_revenue

def calc_total(target_date = None):
    all_parks = get_all_parks()
    sum = 0
    park_level = {}
    for park in all_parks:
        revenue = calc_revenue(park, target_date)
        sum += revenue
        park_level[park] = revenue
    return sum, park_level