from src.read_data import read_forecast_data, read_price, read_weather_data
from services.constants import price_areas
import json
from src.analysis.determine_status import determine_revenue_grade

from src.calculations.calc_revenue import calc_revenue
from src.calculations.calc_dayahead_revenue import calc_dayahead_revenue
from src.analysis.extreme_price import find_extreme_prices


def determine_loss_factors(park_name, adjusted_revenue, extreme_price_timestamps, target_day = None, dayahead_revenue = None):
    forecast_data = read_forecast_data(park_name, target_day, False)
    predicted_volume = forecast_data[0]
    produced_volume = forecast_data[1]
    bought_volume = [predicted-produced for predicted, produced in zip(predicted_volume, produced_volume)]
    price_area = price_areas().get(park_name)
    reg_price = list(read_price('reg', price_area, target_day)['value'])
    with open("files/price_medians.json") as f:
        price_stats = json.load(f)
        
    reg_status = 0
    savings = 0
    
    no_volume = [vol for vol in produced_volume if vol == 0]
    no_volume_flag = False
    if len(no_volume)>20:
        no_volume_flag = True
    
    
    if price_stats:
        reg_medians = price_stats.get('reg').get('median').get(price_area)
        reg_stdev = price_stats.get('reg').get('std').get(price_area)
        
        reg_sell = [i for price, median, stdev, volume, i in zip(reg_price, reg_medians, reg_stdev, bought_volume, range(24)) if abs(median-price)>stdev and volume<0]
        reg_buy = [i for price, median, stdev, volume, i in zip(reg_price, reg_medians, reg_stdev, bought_volume, range(24)) if (price-median)>stdev and volume>0]
        test = [(median-price)/stdev for price, median, stdev, volume, i in zip(reg_price, reg_medians, reg_stdev, bought_volume, range(24))]
        if len(reg_buy)>0 or len(reg_sell)>0:
            use_reg_buy = reg_buy
            use_reg_sell = reg_sell
            reg_status = 1
            reg_sell = [index for price, median, stdev, volume, index in zip(reg_price, reg_medians, reg_stdev, bought_volume, range(24)) if (median-price)>5*stdev and volume<0]
            reg_buy = [index for price, median, stdev, volume, index in zip(reg_price, reg_medians, reg_stdev, bought_volume, range(24)) if (price-median)>5*stdev and volume>0]
            if len(reg_buy)>0 or len(reg_sell)>0:
                #use_reg_buy = reg_buy
                #use_reg_sell = reg_sell
                reg_status = 2
                reg_sell = [index for price, median, stdev, volume, index in zip(reg_price, reg_medians, reg_stdev, bought_volume, range(24)) if (median-price)>10*stdev and volume<0]
                reg_buy = [index for price, median, stdev, volume, index in zip(reg_price, reg_medians, reg_stdev, bought_volume, range(24)) if (price-median)>10*stdev and volume>0]
                if len(reg_buy)>0 or len(reg_sell)>0:
                    #use_reg_buy = reg_buy
                    #use_reg_sell = reg_sell
                    reg_status = 3
        
        reg_periode = 0
        prediction_offset_severity = 0
        explanation_weather_sets = []
        if reg_status>0:
            buy_cost_today = sum([buy_volume*price for buy_volume, price, i in zip(bought_volume, reg_price, range(24)) if not i in extreme_price_timestamps])
            buy_cost_normal = 0
            test = 0
            for buy_volume, price, normal_price, i in zip(bought_volume, reg_price, reg_medians, range(24)):
                if i in extreme_price_timestamps:
                    test +=buy_volume*normal_price
                    buy_cost_normal +=0
                elif i in use_reg_buy or i in use_reg_sell:
                    buy_cost_normal +=buy_volume*normal_price
                    test +=buy_volume*normal_price
                else:
                    buy_cost_normal +=buy_volume*price
                    test +=buy_volume*price
            savings = buy_cost_today-buy_cost_normal
            
            if len(use_reg_sell)>0 and len(use_reg_buy)>0:
                reg_periode = 2
            else:
                if len(use_reg_sell)>0: relevant_list = use_reg_sell
                else: relevant_list = use_reg_buy
                connected = True
                for timestep_idx in range(len(relevant_list)):
                    if timestep_idx!=len(relevant_list)-1:
                        if relevant_list[timestep_idx+1]-relevant_list[timestep_idx]>1: connected = False
                if connected: reg_periode = 1
                else: 
                    reg_periode = 2
            
        with open("files/production_stats.json") as f:
            production_stats = json.load(f)
        medians = production_stats.get("diff").get("median").get(park_name)
        stds = production_stats.get("diff").get("std").get(park_name)
            
        difference = [-volume for volume in bought_volume]
        relative_difference = [(median-diff)/std for diff, median, std in zip(difference, medians, stds)]
        meaningful_differences = [i for diff, i in zip(relative_difference, range(24)) if diff>1]
        big_differences = [i for diff, i in zip(relative_difference, range(24)) if diff>2]
        huge_differences = [i for diff, i in zip(relative_difference, range(24)) if diff>3]
        prediction_offset_severity = len([l for l in [meaningful_differences, big_differences, huge_differences] if len(l)>0])
        if prediction_offset_severity>0:
                """if prediction_offset_severity == 1: relevant_list = meaningful_differences
                elif prediction_offset_severity == 2: relevant_list = big_differences
                else: relevant_list = huge_differences"""
                relevant_list = meaningful_differences
                weather_sets = read_weather_data(park_name)
                for weather_data in weather_sets:
                    service = weather_data.get('title')[15:-len(park_name)-5]
                    predicted = weather_data.get('datasets')[0].get('data')
                    actual = weather_data.get('datasets')[1].get('data')
                    weather_change = [pred-real for pred, real, i in zip(predicted, actual, range(24)) if i in relevant_list]
                    if len([wc for wc in weather_change if wc>0])>=len(weather_data)/2:
                        explanation_weather_sets.append(service)
                    
        new_revenue = adjusted_revenue+savings
        grade = determine_revenue_grade(new_revenue, dayahead_revenue, park_name)
        return reg_status, grade, savings, reg_periode, prediction_offset_severity, explanation_weather_sets, no_volume_flag
    else:
        return None
    


park_name = 'maalarberget'
revenue = calc_revenue(park_name)
dayahead = calc_dayahead_revenue(park_name)
critical_timesteps, updated_grade, profit_loss = find_extreme_prices(park_name)
spot_status, reg_status, grade, savings = determine_loss_factors(park_name, revenue+profit_loss, critical_timesteps, dayahead_revenue=dayahead)
