from services.parks_list import get_unprofitable_parks, get_all_parks
from src.calculations.calc_total import calc_total
from src.calculations.calc_dayahead_revenue import calc_dayahead_revenue
from src.analysis.determine_status import determine_revenue_grade, determine_offset
from services.parks_list import get_all_parks
from src.read_data import read_availability_data
from src.analysis.park_imbalance_lists import imbalance_volume, dayahead_earning, actual_earning
from services.load_stats import load_revenue_diff_median, load_revenue_diff_stdev
from random import randint

volume_median = -200
volume_stdev = 2000

def generate_dashboard_data():
    all_parks = get_all_parks()
    total_availability_drop = 0
    total_promised_availability = 0
    total_imbalance_volume = 0
    total_imbalance_cost = 0
    
    for park in all_parks:
        promised_availability, actual_availability = read_availability_data(park, json=False)
        availability_drop = [p-a for p, a in zip(promised_availability, actual_availability) if p>a]
        total_promised_availability += sum(promised_availability)
        total_availability_drop += sum(availability_drop)
        total_imbalance_volume += sum(imbalance_volume(park))
        expected_earning  = sum(dayahead_earning(park))
        earning = sum(actual_earning(park))
        total_imbalance_cost += expected_earning-earning
    
    if total_imbalance_cost<load_revenue_diff_median('total'): 
        cost_sign = "-"
        cost_color  = "success"
    else:
        cost_sign = "+"
        cost_color  = "error"
    
    if total_imbalance_volume<volume_median: 
        volume_sign = "-"
        volume_color  = "success"
    else:
        volume_sign = "+"
        volume_color  = "error"
    
    
    return {
        "data": [
        {"title": "Imbalance Cost", "value": '{:,}'.format(int(total_imbalance_cost)).replace(',', ' '), "offset": cost_sign+str(int(((abs(total_imbalance_cost-load_revenue_diff_median('total')))/load_revenue_diff_stdev('total'))*100))+"%", "color": cost_color},
        {"title": "Imbalance Volume", "value": '{:,}'.format(int(total_imbalance_volume)).replace(',', ' ')+" MW", "offset": volume_sign+str(int(((abs(total_imbalance_volume-volume_median)/volume_stdev))*100))+"%", "color": volume_color},
        {"title": "Data Availability", "value": "100%"},
        {"title": "Park Availability", "value": str(100-int((total_availability_drop/total_promised_availability)*100))+"%"}]
    }
    
