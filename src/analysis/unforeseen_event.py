from src.read_data import read_forecast_data, read_wind_data

def unforeseen_event(park_name, target_date = None):
        forecast, actual = read_forecast_data(park_name, target_date, json = False)
        
        actual_wind = read_wind_data(park_name, target_date, json = False)[0]
        
        suspect_hours = []
        connecting_hours = []

        #print(" ")
        for i in range(24):
                wind = actual_wind[i]
                f = forecast[i]
                a = actual[i]
                #print(f"{wind}, {f}, {a}")
                if (wind > 6 and f > 30 and a <= 0.5 * f) or (a<=0.5 and wind>4):
                        suspect_hours.append(i)
        for hour in suspect_hours:
                if hour+1 in suspect_hours or hour==24 or hour== suspect_hours[-1]:
                        connecting_hours.append(hour)
        return connecting_hours