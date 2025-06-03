from src.analysis.determine_loss_factors import determine_loss_factors
from src.analysis.explain_volume_imbalance import explain_volume_imbalance
from services.constants import price_areas
from services.parks_list import get_unprofitable_parks
from src.analysis.unforeseen_event import unforeseen_event
from services.constants import get_date
from src.analysis.determine_status import determine_offset, determine_revenue_grade, determine_volume_grade
from datetime import datetime
from src.calculations.calc_revenue import calc_revenue
from src.calculations.calc_dayahead_revenue import calc_dayahead_revenue
from src.read_data import read_forecast_data
from services.parks_list import get_unprofitable_parks, get_all_parks
import numpy as np
from src.read_data import read_price, read_intraday_volumes
from src.analysis.critical_revenue_loss_hours import get_critical_hours
from src.analysis.blame_list_hours import get_blame_hours
from src.analysis.park_imbalance_lists import actual_earning, dayahead_earning
from src.analysis.extreme_prices import find_extreme_prices


def enter_new_line(str):
    parts = str.split('\n')
    output_str = ""
    for part in parts:
        str_list = part.split()
        character_limit = 32
        current_char_count = 0
        final_str = ""
        this_str_part = ""
        for word in str_list:
            if word == "Ubalansekostnad":
                final_str = final_str+"\n"+this_str_part
                this_str_part = "\n"+word
                current_char_count = len(word)
            elif current_char_count+len(word)+1<character_limit:
                this_str_part = this_str_part+" "+word
                current_char_count += (len(word)+1)
            else:
                final_str = final_str+"\n"+this_str_part
                this_str_part = word
                current_char_count = len(word)
        final_str = final_str+"\n"+this_str_part
        output_str = output_str+final_str
    return output_str

def list_to_str(list):
    if len(list)==0:
        return ""
    elif len(list)==1:
        return list[0].capitalize()
    else:
        return_str = list[0]
        for index in range(len(list[1:])):
            if index == len(list)-2:
                return_str = return_str+" and "+list[index+1]
            else:
                return_str = return_str+", "+list[index+1]
        return return_str


def format_norwegian_date(date_obj):
    norwegian_months = {
        1: "januar", 2: "februar", 3: "mars", 4: "april",
        5: "mai", 6: "juni", 7: "juli", 8: "august",
        9: "september", 10: "oktober", 11: "november", 12: "desember"
    }

    return f"{date_obj.day}. {norwegian_months[date_obj.month]} {date_obj.year}"

    
def coherent_list(list):
    if len(list)>1:
        last_step = list[0]
        for item in list[1:]:
            if item-last_step != 1: return False
            last_step = item
        return True
    else: return True
    
def sort_parks(list, cost_dict):
    red_parks = sorted([p for p in list if p.get('color').get('imbalancecost') == 'error'], key=lambda x: cost_dict.get(x.get('park')))
    yellow_parks = sorted([p for p in list if p.get('color').get('imbalancecost') == 'warning'], key=lambda x: cost_dict.get(x.get('park')))
    green_parks = sorted([p for p in list if p.get('color').get('imbalancecost') == 'success'], key=lambda x: cost_dict.get(x.get('park')))

    return red_parks + yellow_parks + green_parks

def get_hd_day_report():
    loss_factors = determine_loss_factors()
    unprofitable_parks = get_unprofitable_parks()
    
    if len(unprofitable_parks)>0: 
        subtitle = f"Today there were big imbalance costs in {list_to_str(list([key.replace('aa', 'å').capitalize() for key in unprofitable_parks.keys()]))}. "
    else: 
        subtitle = "Today there were no big imbalance costs.. "
    high_volume_imbalance_parks = [park for park, data in loss_factors.items() if data.get('volume_abnormality') and park not in unprofitable_parks]
    subtitle = subtitle+f"Also imbalance volume in {list_to_str(high_volume_imbalance_parks)}."
    
    lf = determine_loss_factors()
    rows = []
    cost_dict = {}
    for p in lf.keys():
        if lf.get(p).get('volume_abnormality'):
            xp = find_extreme_prices(price_areas().get(p))
            if len(xp)>0: arsak = "extreme prices and"
            less_wind, model_disagreement, availability_reduction, icing = explain_volume_imbalance(p)
            if len(lf.get(p).get('abnormally_low_production_hours'))>2: arsak = 'icing'
            else:
                if less_wind or model_disagreement:
                    arsak = "forecast dev"
                elif availability_reduction:
                    arsak = "reduced availability"
                else:
                    arsak = "icing"
            if len(xp)>0: arsak = "extreme prices and "+arsak
        else:
            arsak = "high prices"
        dayahead_vol, prod_vol = read_forecast_data(p, json = False)
        revenue = calc_revenue(p)
        dayahead_revenue = calc_dayahead_revenue(p)
        cost_dict[p] = revenue-dayahead_revenue
        
        imbalancevolume = int(round(sum(prod_vol)-sum(dayahead_vol)))
        formatted_imbalancevolume = f"{imbalancevolume:,} MW".replace(",", " ")
        
        imbalancecost = int(round(revenue - dayahead_revenue))
        formatted_imbalancecost = f"€ {imbalancecost:,}".replace(",", " ")
        
        if determine_revenue_grade(revenue, dayahead_revenue, p)!="success" or determine_volume_grade(sum(prod_vol), sum(dayahead_vol), p) != "success" or arsak =="icing":
            rows.append({
                'pricearea': price_areas().get(p),
                'park': p,
                'imbalancevolume': formatted_imbalancevolume,
                'imbalancecost': formatted_imbalancecost,
                'cause': arsak,
                'color': {"imbalancecost": determine_revenue_grade(revenue, dayahead_revenue, p), 'imbalancevolume': determine_volume_grade(sum(prod_vol), sum(dayahead_vol), p)}
                },)
            
    
    columns = [
        { 'name': "park", 'align': "left" },
        { 'name': "imbalancevolume", 'align': "left" },
        { 'name': "imbalancecost", 'align': "left" },
        { 'name': "cause", 'align': "right" },
    ]
    
    
    blame = {'columns': columns, 'rows': sort_parks(rows, cost_dict)}
    
    all_parks = get_all_parks()
    loss_factors = determine_loss_factors()
    all_dayahead_earnings = []
    all_actual_earnings = []
    labels = read_forecast_data(all_parks[0]).get("labels")
        
    for park in all_parks:
            dayahead_earnings = dayahead_earning(park)
            all_dayahead_earnings.append(dayahead_earnings)
            actual_earnings = actual_earning(park)
            all_actual_earnings.append(actual_earnings)
    
    date = get_date()
    worst_hours, loss_amount = get_critical_hours(date)
    
    hourly_blame, parks_to_blame = get_blame_hours(date)
    if len(worst_hours)>0:
        cleaned_pb = [item.strip() for item in parks_to_blame if item.strip()]
        wp_list = [f"{list_to_str([item.strip() for item in parks_to_blame.get(p) if item.strip()])} at {p.capitalize()}" for p in cleaned_pb]
        wp_str = list_to_str(wp_list)+" in"
        wp_str = str(int(round(loss_amount, 2)*100))+f"% of costs are due to {list_to_str(wp_list)} in the highlighted timesteps."
    else:
        wp_str = "No large imbalance costs"
    
    if len(worst_hours)>0:
        xmin = int(worst_hours[0])
        xmax = int(worst_hours[-1])
    else:
        xmin = None
        xmax = None
    
    
    graph ={
            "title": "Income overview",
            "description": wp_str,
            "labels": labels,
            "datasets": [{"label": "Dayahead revenue", "color": "light", "data": np.cumsum(np.array(all_dayahead_earnings).sum(axis=0)).tolist(), "meta": hourly_blame}, 
                         {"label": "Total revenue", "color": "info","data":np.cumsum(np.array(all_actual_earnings).sum(axis=0)).tolist()}],
            "xAxis": "Time",
            "yAxis": "Euro revenue",
            "annotation": {
                "xMin": xmin,
                "xMax": xmax,
                "label": "critical hours"
               }
        }
    
    if len(unprofitable_parks)>0: 
        title = 'High imbalance costs'
    else:
        title = 'Low imbalance costs'
        subtitle = 'There were no high prices or imbalance costs today. '
    return {'title': title, 'subtitle': subtitle, 'blame': blame, 'graph': graph}
