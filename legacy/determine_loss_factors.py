from src.read_data import read_forecast_data, read_price, read_weather_data
from services.constants import price_areas, get_date
import json
from src.analysis.determine_status import determine_revenue_grade
import pandas as pd
from src.calculations.calc_revenue import calc_revenue
from src.calculations.calc_dayahead_revenue import calc_dayahead_revenue
from src.analysis.extreme_price import find_extreme_prices
from itertools import combinations

def test_hypothesis(park_name, hypothesis, high_price_hours, high_volume_diff_hours, no_production_hours, reg_prices, unbalance_volume, extreme_price_timesteps, adjusted_revenue, dayahead):
    key_word_to_relevant_timesteps = { 'availability': no_production_hours, 'volume': high_volume_diff_hours, 'price': high_price_hours}
    if len(hypothesis)>2:
        relevant_hours = [i for i in high_price_hours if i in high_volume_diff_hours and i in no_production_hours]
        critical_hours = [i for i in relevant_hours if (reg_prices[i]<0 and unbalance_volume[i]<0) or (reg_prices[i]>0 and unbalance_volume[i]>0)]
        cost = 0
        for h in relevant_hours:
            volume = unbalance_volume[h]
            price = reg_prices[h]
            if not h in extreme_price_timesteps:
                cost += volume*price
        grade = determine_revenue_grade(adjusted_revenue+cost, dayahead, park_name)
    if len(hypothesis)>1:
        relevant_hours = [i for i in key_word_to_relevant_timesteps.get(hypothesis[0]) if i in key_word_to_relevant_timesteps.get(hypothesis[1])]
        critical_hours = [i for i in relevant_hours if (reg_prices[i]<0 and unbalance_volume[i]<0) or (reg_prices[i]>0 and unbalance_volume[i]>0)]
        cost = 0
        for h in critical_hours:
            volume = unbalance_volume[h]
            price = reg_prices[h]
            if not h in extreme_price_timesteps:
                cost += volume*price
        grade = determine_revenue_grade(adjusted_revenue+cost, dayahead, park_name)
    else:
        hyp = hypothesis[0]
        critical_hours = key_word_to_relevant_timesteps.get(hyp)
        cost = 0
        for h in critical_hours:
            volume = unbalance_volume[h]
            price = reg_prices[h]
            if not h in extreme_price_timesteps:
                cost += volume*price
        grade = determine_revenue_grade(adjusted_revenue+cost, dayahead, park_name)
    return cost, grade
    


def determine_loss_factors(park_name, adjusted_revenue, extreme_price_timestamps, target_day = None, dayahead_revenue = None):
    
    blame = []
    if not target_day: target_day = get_date()
        
    
    #Loading necessary data
    with open("files/price_stats.json") as f:
        price_stats = json.load(f)
    with open("files/production_stats.json") as f:
        production_stats = json.load(f)
    price_area = price_areas().get(park_name)
    reg_median = price_stats.get('reg').get('median').get(price_area)
    reg_std = price_stats.get('reg').get('std').get(price_area)
    actual_reg_prices = read_price('reg', price_area).value.values.tolist()
    actual_spot_prices = read_price('spot', price_area).value.values.tolist()
    dayahead, prod = read_forecast_data(park_name, json = False)
    production_deviation_median = production_stats.get("diff").get("median").get(park_name)
    production_deviation_std = production_stats.get("diff").get("std").get(park_name)
    
    
    #Hours with no produced volume
    no_volume_hours = [i for t, i in zip(prod, range(24)) if t == 0]
    num_no_volume_hours = len(no_volume_hours)
    if num_no_volume_hours>0:
        blame.append('availability')
    
    #Determining status for regulation price
    reg_price_deviation = [abs(price-reg_median)/reg_std for price in actual_reg_prices]
    
    if max(reg_price_deviation)<1: 
        reg_status = 0
    elif max(reg_price_deviation)<5: 
        reg_status = 1
    elif max(reg_price_deviation)<10: 
        reg_status = 2
    else: 
        reg_status = 3
    if reg_status>0:
        blame.append("price")
    
    #Determining price_period
    high_reg_timesteps = [i for i, reg in zip(range(24), reg_price_deviation) if reg>1]
    connected = True
    for ts in range(len(high_reg_timesteps)):
        if high_reg_timesteps[ts]!=high_reg_timesteps[-1]:
            if high_reg_timesteps[ts+1]-high_reg_timesteps[ts]>1: connected = False
    if len(high_reg_timesteps)==0: reg_periode = 0
    elif connected: reg_periode = 1
    else: reg_periode = 2
    
    #Determining severity of prediction offset
    unbalance_volume = [promised-produced for promised, produced in zip(dayahead, prod)]
    total_unbalance_volume = sum(unbalance_volume)
    unbalance_offset = abs(total_unbalance_volume-production_deviation_median)/production_deviation_std
    if unbalance_offset<1: prediction_offset_severity = 0
    elif unbalance_offset<2: prediction_offset_severity = 1
    elif unbalance_offset<3: prediction_offset_severity = 2
    else: prediction_offset_severity = 3
    explanation_weather_sets = []
    lower_production = [i for i, promised, produced in zip(range(24), dayahead,prod) if promised-produced>0]
    replan_improvement = 0
    if prediction_offset_severity>0:
        blame.append('volume')
        weather_sets = read_weather_data(park_name)
        for weather_data in weather_sets:
            service = weather_data.get('title')[15:-len(park_name)-5]
            predicted = weather_data.get('datasets')[0].get('data')
            actual = weather_data.get('datasets')[1].get('data')
            weather_change = [pred-real for pred, real, i in zip(predicted, actual, range(24)) if i in lower_production]
            if len([wc for wc in weather_change if wc>0])>=len(weather_data)/2:
                explanation_weather_sets.append(service)
        if park_name == 'maalarberget': replan_df = pd.read_csv('aneo_data/målarberget_forecasts.csv')
        else: replan_df = pd.read_csv(f'aneo_data/{park_name}_forecasts.csv')
        replan_df["time"] =  pd.to_datetime(replan_df["time"])
        replan_df["date"] = replan_df["time"].dt.date
        replan_values = replan_df[(replan_df['date']==target_day) & (replan_df["forecast"]== "replan")][" "].values.tolist()
        replan_volume = [promised-replanned for promised, replanned in zip(dayahead, replan_values)]
        total_replan_volume = sum(replan_volume)
        replan_improvement = total_replan_volume/total_unbalance_volume
        
        
                
    #Determine cost
    if len(blame)>0:
        if len(blame)==3:
            blame_tuple = [tuple(blame)]
            two_combos = list(combinations(blame, 2))
            this = blame_tuple+(two_combos)
            hypothesis = [tuple(blame)]+list(combinations(blame, 2))+(list(combinations(blame, 1)))
        elif len(blame)>1:hypothesis = [tuple(blame)] + list(combinations(blame, 1))
        else: hypothesis = [tuple(blame)]
        winning_hyp = hypothesis[0]
        cost = 0
        grade = 'error'
        for hyp in hypothesis:

            hyp_cost, hyp_grade = test_hypothesis(park_name, hyp, high_reg_timesteps, lower_production, no_volume_hours, actual_reg_prices, unbalance_volume, extreme_price_timestamps, adjusted_revenue, dayahead_revenue)
            if hyp_cost>cost: 
                winning_hyp = hyp
                cost = hyp_cost
                grade = hyp_grade
        blame = winning_hyp
            
    else:
        grade = "error"
        cost = 0
        

    
    
    
    
    return blame, num_no_volume_hours, reg_status, reg_periode, prediction_offset_severity, explanation_weather_sets, replan_improvement, cost, grade
    

"""
park_name = 'maalarberget'
revenue = calc_revenue(park_name)
dayahead = calc_dayahead_revenue(park_name)
critical_timesteps, updated_grade, profit_loss = find_extreme_prices(park_name)
determine_loss_factors(park_name, revenue+profit_loss, critical_timesteps, dayahead_revenue=dayahead)"""