from os import listdir
import unicodedata
from src.calculations.calc_revenue import calc_revenue
from src.calculations.calc_dayahead_revenue import calc_dayahead_revenue
from src.analysis.determine_status import determine_offset, determine_revenue_grade

def normalize(list):
    new_list = []
    for word in list:
        normalized_word = unicodedata.normalize("NFC", word).replace('å', 'aa')
        new_list.append(normalized_word)
    return new_list

def get_all_parks():
    list = listdir('./aneo_data')
    forecast_parks = normalize(sorted([file[:-14] for file in list if file[-13:] == 'forecasts.csv']))
    parkdata_parks = normalize(sorted([file[:-14] for file in list if file[-13:] == 'park_data.csv']))    
    tilgjengelighet_parks = normalize(sorted([file[:-20] for file in list if file[-19:] == 'tilgjengelighet.csv']))
    værmelding_parks = normalize(sorted([file[:-15] for file in list if file[-14:] == 'værmelding.csv']))

    return [park for park in forecast_parks if (park in tilgjengelighet_parks and park in værmelding_parks and park in parkdata_parks)]
    #return parkdata_parks

def get_unprofitable_parks():
    all_parks = get_all_parks()
    under = {}
    for park in all_parks:
        revenue = calc_revenue(park)
        dayahead = calc_dayahead_revenue(park)
        os = determine_offset(revenue, park_name=park, dayahead_revenue=dayahead)
        grade = determine_revenue_grade(revenue, dayahead_revenue=dayahead, park_name=park)
        if grade in ['error', 'warning']: under[park] = [os, grade]
    return under
    