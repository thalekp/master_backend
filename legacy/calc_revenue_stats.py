import pandas as pd
from src.calculations.calc_revenue import calc_revenue
from src.calculations.calc_dayahead_revenue import calc_dayahead_revenue
import statistics
import json

def store_park_revenue_stats(parks):
    all_data = {}
    all_stats = {}

    for park in parks:
        df = pd.read_csv(f"aneo_data/{park.replace('aa', 'å')}_forecasts.csv")
        df.columns = [c.strip() for c in df.columns]
        dayahead = df[df["forecast"] == "dayahead"].copy()
        dayahead["time"] = pd.to_datetime(dayahead["time"])
        all_dates = sorted(dayahead["time"].dt.date.unique(), reverse=True)
        #all_dates = sorted(dayahead["time"].dt.date.unique(), reverse=True)[0:10]
        all_revenue = [calc_revenue(park, day) for day in all_dates[2:]]
        all_dayahead_revenue = [calc_dayahead_revenue(park, day) for day in all_dates[2:]]
        difference = [revenue-dayahead_revenue for revenue, dayahead_revenue in zip(all_revenue, all_dayahead_revenue)]
        all_data[park] = {'all_revenue': all_revenue,
                          'difference' : difference}
    for park in parks:
        park_stats = {}
        park_stats['median'] = statistics.median(all_data.get(park).get('all_revenue'))
        park_stats['mean'] = statistics.mean(all_data.get(park).get('all_revenue'))
        park_stats['stdev'] = statistics.stdev(all_data.get(park).get('all_revenue'))
        park_stats['diff_median'] = statistics.median(all_data.get(park).get('difference'))
        park_stats['diff_mean'] = statistics.mean(all_data.get(park).get('difference'))
        park_stats['diff_stdev'] = statistics.stdev(all_data.get(park).get('difference'))
        all_stats[park] = park_stats
        
    total_revenue = [sum([all_data.get(park).get('all_revenue')[i] for park in list(all_data.keys())]) for i in range(len(all_data.get(parks[0]).get('all_revenue')))]
    total_difference = [sum([all_data.get(park).get('difference')[i] for park in list(all_data.keys())]) for i in range(len(all_data.get(parks[0]).get('difference')))]
    
    all_stats['total'] = {
        'median' : statistics.median(total_revenue),
        'mean' : statistics.mean(total_revenue),
        'stdev': statistics.stdev(total_revenue),
        'diff_median' : statistics.median(total_difference),
        'diff_mean' : statistics.mean(total_difference),
        'diff_stdev': statistics.stdev(total_difference)
    }

    with open("files/stats.json", "w") as f:
        json.dump(all_stats, f, indent=2)
        
store_park_revenue_stats(['klevberget', 'maalarberget', 'roan'])