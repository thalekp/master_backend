import pandas as pd
from src.calculations.calc_revenue import calc_revenue
from src.calculations.calc_dayahead_revenue import calc_dayahead_revenue
import statistics

def store_park_revenue_stats(parks):
    all_data = {}
    all_stats = []

    for park in parks:
        df = pd.read_csv(f"aneo_data/{park.replace('aa', 'å')}_forecasts.csv")
        df.columns = [c.strip() for c in df.columns]
        dayahead = df[df["forecast"] == "dayahead"].copy()
        dayahead["time"] = pd.to_datetime(dayahead["time"])
        all_dates = sorted(dayahead["time"].dt.date.unique(), reverse=True)

        all_revenue = [calc_revenue(park, day) for day in all_dates[2:]]
        all_dayahead_revenue = [calc_dayahead_revenue(park, day) for day in all_dates[2:]]
        difference = [revenue - dayahead_revenue for revenue, dayahead_revenue in zip(all_revenue, all_dayahead_revenue)]

        all_data[park] = {'all_revenue': all_revenue, 'difference': difference}

        park_stats = {
            'park': park,
            'median': statistics.median(all_revenue),
            'mean': statistics.mean(all_revenue),
            'stdev': statistics.stdev(all_revenue),
            'diff_median': statistics.median(difference),
            'diff_mean': statistics.mean(difference),
            'diff_stdev': statistics.stdev(difference)
        }

        all_stats.append(park_stats)

    # Total aggregated stats
    total_revenue = [sum([all_data[park]['all_revenue'][i] for park in parks]) for i in range(len(all_data[parks[0]]['all_revenue']))]
    total_difference = [sum([all_data[park]['difference'][i] for park in parks]) for i in range(len(all_data[parks[0]]['difference']))]


    total_stats = {
        'park': 'total',
        'median': statistics.median(total_revenue),
        'mean': statistics.mean(total_revenue),
        'stdev': statistics.stdev(total_revenue),
        'diff_median': statistics.median(total_difference),
        'diff_mean': statistics.mean(total_difference),
        'diff_stdev': statistics.stdev(total_difference)
    }

    all_stats.append(total_stats)

    stats_df = pd.DataFrame(all_stats)
    stats_df.to_csv("files/revenue_stats.csv", index=False)

store_park_revenue_stats(['klevberget', 'maalarberget', 'roan', 'trattberget', 'lyckaas', 'frøya'])
