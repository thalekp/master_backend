from services.parks_list import get_unprofitable_parks
from src.calculations.calc_total import calc_total
from src.calculations.calc_dayahead_revenue import calc_dayahead_revenue
from src.analysis.determine_status import determine_revenue_grade, determine_offset
from services.parks_list import get_all_parks



def generate_dashboard_data():
    parks = get_unprofitable_parks()
    total, park_revenues = calc_total()
    dayahead = sum([calc_dayahead_revenue(park) for park in get_all_parks()])
    revenues = [total]
    grades = [determine_revenue_grade(total, dayahead_revenue=dayahead)]
    offsets = [determine_offset(total, dayahead_revenue=dayahead)[0]]
    absolute_offsets = [total-dayahead]
    
    for park in parks:
        revenue = park_revenues.get(park)
        revenues.append(revenue)
        grades.append(parks.get(park)[1])
        offsets.append(parks.get(park)[0][0])
        total +=revenue
        absolute_offsets.append(revenue-calc_dayahead_revenue(park))
    labels = ["total"]
    labels.extend(list(parks.keys()))
        
    return {
        "labels": labels,
        "datasets": [
            {
                "label": "Revenues",
                "color": "info",
                "data": revenues
            },
            {
                "label": "Grades",
                "color": "info",
                "data": grades
            },
            {
                "label": "Offsets",
                "color": "info",
                "data": offsets
            },
            {
                "label": "Absolute Offset",
                "color": "info",
                "data": absolute_offsets
            }
        ]
    }