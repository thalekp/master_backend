from src.read_data import read_forecast_data, read_price
from services.constants import price_areas
from services.parks_list import get_all_parks
from src.analysis.extreme_prices import find_extreme_prices
from services.constants import price_areas
from src.analysis.unforeseen_event import unforeseen_event
from src.analysis.critical_revenue_loss_hours import get_critical_hours

def get_blame_hours(target_date):
    all_parks = get_all_parks()
    price_area_dict = price_areas()
    worst_hours = get_critical_hours(target_date)[0]
    print(f"Worst hours: {worst_hours}")


    produced_volumes = []
    revenue_differences = {}

    for park in all_parks:
        price_area = price_area_dict.get(park)
        dayahead, prod = read_forecast_data(park, target_date, json = False)
        
        spot_price = read_price('spot', price_area, target_date)['value'].values
        reg_price = read_price('reg', price_area, target_date)['value'].values
        
        prod_difference = [p-d for p,d in zip(prod, dayahead)]
        produced_volumes.append(prod_difference)
        
        predicted_revenue = [sp*dh for sp, dh in zip(spot_price, dayahead)]
        imbalance_cost = [rp*(p-d)+pr for rp, p, d, pr in zip(reg_price, prod, dayahead, predicted_revenue)]
        revenue_differences[park] = imbalance_cost

    blame_list = []
    parks_to_blame = {} 
    for hour in range(len(revenue_differences.get(all_parks[0]))):
        largest_cost = float('inf')
        total_cost = 0
        for park in all_parks:
            park_revenue = revenue_differences.get(park)[hour]
            if park_revenue < 0: total_cost += park_revenue
            if park_revenue < largest_cost:
                largest_cost = park_revenue
                blame_park = park
                
        if total_cost<0: 
            cause_str = ""
            binding_word = ""
            location_word = ""
            pa = price_areas().get(blame_park)
            x_p = find_extreme_prices(pa, target_date)
            ue = unforeseen_event(blame_park, target_date)
            if hour in x_p:
                cause_str = "extreme prices "
                binding_word = "and "
                location_word = " at "
            if hour in ue:
                cause_str = f"{cause_str}{binding_word}icing "
                location_word = " at "
            
            blame_list.append(f"{int(round(min(largest_cost/total_cost, 1.0), 2)*100)}% of cost because of {cause_str}{location_word}{blame_park.capitalize()}")
            
            if hour in worst_hours:
                if blame_park in parks_to_blame.keys():
                    parks_to_blame[blame_park] = parks_to_blame.get(blame_park)+[cause_str]
                else:
                    parks_to_blame[blame_park] = [cause_str]
        else: blame_list.append("all parks have positive revenue")
    return blame_list, parks_to_blame




