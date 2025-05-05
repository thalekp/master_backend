import pandas as pd
from datetime import datetime

def get_date():
    df = pd.read_csv(f"aneo_data/roan_forecasts.csv")
    dayahead = df[df["forecast"] == "dayahead"].copy()
    dayahead["time"] = pd.to_datetime(dayahead["time"])
    all_dates = sorted(dayahead["time"].dt.date.unique(), reverse=True)
    #7. januar
    #target_day = all_dates[71]
    #9. januar
    #TRICKY
    #target_day = all_dates[69]
    #21. januar
    #target_day = all_dates[57]
    #23. januar
    #target_day = all_dates[55]
    #24. januar
    #target_day = all_dates[54]
    #25. januar
    #TRICKY
    #target_day = all_dates[53]
    #26. januar
    #target_day = all_dates[52]
    #4. februar
    #target_day = all_dates[43]
    #19. februar
    #TRICKY DAG
    #INTRAHANDELARKEDTING
    #target_day = all_dates[28]
    #4. mars
    #target_day = all_dates[15]
    date_str = list(pd.read_csv("files/date.csv")['date'].values)[0]
    target_day = datetime.strptime(date_str, "%Y-%m-%d").date()
    return target_day

def price_areas():
    return {'roan': 'NO3', 'klevberget': 'SE2', 'maalarberget': 'SE3'}

def price_areas_list():
    return ['NO3', 'SE2', 'SE3']

def get_price_area_parks(price_area):
    if price_area == 'NO3': return ['roan']
    if price_area == 'SE2': return ['klevberget']
    if price_area == 'SE3': return ['maalarberget']