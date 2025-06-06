import pandas as pd
from services.constants import get_date

legend_translation = {'spot': "Spotprice", 
                      'reg': "Regulationprice",
                      'dayahead_reported': "Reported energy production",
                      'prod': "Actual energy production",
                      'replan': "Real time production forecast",
                      'dayahead_planned_avl' : "Dayahead reported availability",
                      'replan_planned_avl': "Actual availability",
                      'ws_meteomatics_dayahead': "Dayahead weather forecast",
                      'ws_arome_dayahead': "Dayahead weather forecast",
                      'ws_dnmi_dayahead': "Dayahead weather forecast",
                      'ws_meteomatics_replan': "Real time weather forecast",
                      'ws_arome_replan': "Real time weather forecast",
                      'ws_dnmi_replan': "Real time weather forecast"}

def read_price(price_type, target_area, target_day=None):
    if price_type in ['spot', 'reg']:
        df = pd.read_csv(f"aneo_data/{price_type}pris.csv")
        df["time"] =  pd.to_datetime(df["time"])
        if not target_day:
            target_day = get_date()
        df_day = df[(df["time"].dt.date==target_day) & (df["area"] == target_area)].copy()
        all_hours = pd.date_range("00:00", "23:00", freq="1h").strftime("%H:%M")

        df_day["time"] = df_day["time"].dt.strftime("%H:%M")

        df_day = df_day.set_index("time").reindex(all_hours).reset_index().rename(columns={"index": "time"})

        df_day["area"] = df_day["area"].fillna(target_area)
        df_day["value"] = df_day["value"].astype(float).ffill().bfill()
        return df_day
    elif price_type in ['intraday_VWAP_buy', 'intraday_VWAP_sell']:
        df = pd.read_csv(f"aneo_data/{target_area.upper()}_market_data.csv")
        df["time"] =  pd.to_datetime(df["time"])
        if not target_day:
            target_day = get_date()
        df_day = df[(df["time"].dt.date==target_day)].copy()
        all_hours = pd.date_range("00:00", "23:00", freq="1h").strftime("%H:%M")
        df_day = df_day.drop_duplicates(subset="time", keep="first")
        df_day["time"] = df_day["time"].dt.strftime("%H:%M")
        df_day = df_day.set_index("time").reindex(all_hours).reset_index().rename(columns={"index": "time"})

        df_day[price_type] = df_day[price_type].astype(float).ffill().bfill()
        return df_day[price_type]
        
    else: 
        return None

def read_forecast_data(park_name, target_day=None, json = True):
    labels = ["dayahead_reported", "prod"]
    result = csv_to_data(park_name, labels, 'park_data', 'series', 'value', target_day, title = f"Volume produced from {park_name.capitalize()}", json=json, y_axis_name="MWh")
    if not json: return result
    replan = csv_to_data(park_name, ["replan"], 'forecasts', "forecast",' ', target_day)
    replan_dataset = replan.get('datasets')[0]
    replan_dataset['color'] = "light"
    result.get('datasets').append(replan_dataset)
    return result

def read_intraday_volumes(price_area, target_day = None, json = True):
    df = pd.read_csv(f"aneo_data/{price_area.upper()}_market_data.csv")
    if not target_day:
        target_day = get_date()
    all_hours = pd.date_range("00:00", "23:00", freq="1h").strftime("%H:%M")
    labels = ["intraday_vol_buy", "intraday_vol_sell"]
    
    df["time"] = pd.to_datetime(df["time"])
    df = df[df["time"].dt.date == target_day].copy()
    df["time"] = df["time"].dt.strftime("%H:%M")
    df = df.sort_values(by="time")
    df = df.groupby("time", as_index=False).mean(numeric_only=True)
    df = df.set_index("time").reindex(all_hours).reset_index().rename(columns={"index": "time"})
    
    datasets = []
    
    color_dict = {'intraday_vol_buy': 'info', 'intraday_vol_sell': 'dark'}
    
    for label in labels:
        new_set = df.copy()
        new_set[label] = new_set[label].astype(float).ffill().bfill()
        values = new_set[label].fillna(0).round(2).tolist()
        if json:
            datasets.append({
                    "label": f"{legend_translation.get('label')}",
                    "color": color_dict.get(label),
                    "data": values
                })
        else: datasets.append(values)
    if json:
        return {
            "title": f'Intraday volume for {price_area}',
            "labels": all_hours.to_list(),
            "datasets": datasets,
            "xAxis": "Time",
            "yAxis": 'Volume'
        }
    else: 
        return datasets
    

    
def read_availability_data(park_name, target_day = None, json = True):
    labels = ["dayahead_planned_avl", "replan_planned_avl"]
    
    return csv_to_data(park_name, labels, 'tilgjengelighet', "label", "value", target_day, title = f"Availability for {park_name}", json=json, y_axis_name="MWh")
    
def read_wind_data(park_name, target_day = None, json = True):
    labels = ["ws_measured"]
    
    return csv_to_data(park_name, labels, 'park_data', "series", "value", target_day, json=json, y_axis_name="m/s")


def read_weather_data(park_name, target_day = None, json = True, services = None):
    data = []
    arome = csv_to_data(park_name,['ws_arome_dayahead','ws_arome_replan'],'værmelding', "label", "value", target_day, f"Weather forecast from Arome for {park_name.capitalize()}",json=json, y_axis_name='m/s')
    dnmi = csv_to_data(park_name, ['ws_dnmi_dayahead','ws_dnmi_replan'],'værmelding', "label", "value", target_day, f"Weather forecast from DNMI for {park_name.capitalize()}", json=json, y_axis_name='m/s')
    meteomatics = csv_to_data(park_name, ['ws_meteomatics_dayahead','ws_meteomatics_replan'],'værmelding', "label", "value", target_day, f"Weather forecast from Meteomatics for {park_name.capitalize()}", json=json, y_axis_name='m/s')
    ws = [arome, dnmi, meteomatics]
    for w in ws:
        data_available = False
        if json: datasets=w.get("datasets")
        else: datasets = w
        for data_set in datasets:
            if json: data_list = data_set.get("data")
            else: data_list = data_set
            if any(x != 0 for x in data_list):
                data_available = True
        
        if data_available and (not json or not services or (w.get('title')[15:-len(park_name)-5] in services)):
            data.append(w)
            
    return data
    
def csv_to_data(park_name, labels, data_type, label_name, value_name, target_day = None, title = None, json = True, y_axis_name = "yakse"):
    #if park_name == "maalarberget": df = pd.read_csv(f"aneo_data/målarberget_{data_type}.csv")
    df = pd.read_csv(f"aneo_data/{park_name.replace('aa', 'å')}_{data_type}.csv")
    if not target_day:
        target_day = get_date()
    all_hours = pd.date_range("00:00", "23:00", freq="1h").strftime("%H:%M")
    datasets = []
    colors = ['dark','info', 'light']
    
    for idx in range(len(labels)):
        label = labels[idx]
        if labels[idx] in legend_translation.keys():
            legend = legend_translation.get(label)
        else:
            legend = label
        color = colors[idx]
        
                
        #split
        new_set = df[df[label_name] == label].copy()
        new_set["time"] = pd.to_datetime(new_set["time"])
        
        #select date
        new_set = new_set[new_set["time"].dt.date == target_day].copy()
        
        #Remove duplicates, sort by time, fill for all hours
        new_set["time"] = pd.to_datetime(new_set["time"])
        new_set["time"] = new_set["time"].dt.strftime("%H:%M")
        new_set = new_set.sort_values(by="time")
        new_set = new_set.groupby("time", as_index=False).mean(numeric_only=True)
        new_set = new_set.set_index("time").reindex(all_hours).reset_index().rename(columns={"index": "time"})
        new_set[value_name] = new_set[value_name].astype(float).ffill().bfill()
        
        values = new_set[value_name].fillna(0).round(2).tolist()
        
        
        if json:
            datasets.append({
                    "label": f"{legend}",
                    "color": color,
                    "data": values
                })
        else: datasets.append(values)
            
    if json:
        if not title:
            title = f"{data_type.capitalize()} for {park_name.capitalize()}, {target_day}"
        return {
            "title": title,
            "labels": all_hours.to_list(),
            "datasets": datasets,
            "xAxis": "Time",
            "yAxis": y_axis_name
        }
    else: 
        return datasets
    