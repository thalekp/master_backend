from src.calculations.calc_revenue import calc_revenue
from src.calculations.calc_dayahead_revenue import calc_dayahead_revenue
from src.read_data import read_forecast_data, read_price
from services.constants import price_areas
from src.analysis.determine_status import determine_revenue_grade
import statistics

def find_extreme_prices(park_name, target_day = None):
    forecast_data = read_forecast_data(park_name, target_day, False)
    predicted_volume = forecast_data[0]
    produced_volume = forecast_data[1]
    spot_price = list(read_price('spot', price_areas().get(park_name), target_day)['value'])
    reg_price = list(read_price('reg', price_areas().get(park_name), target_day)['value'])
    bought_volume = [produced-predicted for predicted, produced in zip(predicted_volume, produced_volume)]
    profit = [spot*predicted-bought*reg for spot, predicted, bought, reg in zip(spot_price, predicted_volume, bought_volume, reg_price)]
    
    #Extreme reg price
    median_reg = statistics.median(reg_price)
    std_reg = statistics.stdev(reg_price)
    extreme_reg = [i for i,r in enumerate(reg_price) if abs(r-median_reg)>3*std_reg]
    
    #Extreme loss
    median_profit = statistics.median(profit)
    std_profit = statistics.stdev(profit)
    extreme_profit = [i for i,r in enumerate(profit) if abs(r-median_profit)>3*std_profit]
    
    timesteps = [i for i in extreme_reg if i in extreme_profit]
    
    #Determine criticallity level
    profit_loss = sum([profit[i] for i in timesteps])
    revenue = calc_revenue(park_name, target_day)
    dayahead_revenue = calc_dayahead_revenue(park_name, target_day)
    avoided_loss = revenue+profit_loss
    grade = determine_revenue_grade(revenue, dayahead_revenue, park_name)
    updated_grade = determine_revenue_grade(avoided_loss, dayahead_revenue, park_name)

    
    return timesteps, updated_grade, profit_loss