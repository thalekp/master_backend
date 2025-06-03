from services.parks_list import get_unprofitable_parks, get_all_parks
from src.calculations.calc_total import calc_total
from src.calculations.calc_dayahead_revenue import calc_dayahead_revenue
from src.analysis.determine_status import determine_revenue_grade, determine_offset
from services.parks_list import get_all_parks
from src.read_data import read_availability_data


def generate_dashboard_data():
    all_parks = get_all_parks()
    total_availability_drop = 0
    total_promised_availability = 0
    
    for park in all_parks:
        promised_availability, actual_availability = read_availability_data(park, json=False)
        availability_drop = [p-a for p, a in zip(promised_availability, actual_availability) if p>a]
        print("")
        print(park)
        print(sum(availability_drop))
        total_promised_availability += sum(promised_availability)
        total_availability_drop += sum(availability_drop)
    
    return {
        "data": [
        {"title": "Data Availability", "value": "100%"},
        {"title": "park_availability", "value": str(100-int((total_availability_drop/total_promised_availability)*100))+"%"}]
    }
    
print(generate_dashboard_data())