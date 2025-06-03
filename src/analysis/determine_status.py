from services.load_stats import load_revenue_median, load_revenue_diff_median, load_revenue_stdev, load_revenue_diff_stdev, load_diff_production_median, load_diff_production_std
from services.config import get_metric

def determine_revenue_grade(revenue,dayahead_revenue = None, park_name = None):
    if dayahead_revenue: metric = revenue-dayahead_revenue
    else: metric = revenue
    if not park_name: park_name = 'total'

    if get_metric() in ["diff_median", "diff_mean"]:
        median = load_revenue_diff_median(park_name)
        stdev = load_revenue_diff_stdev(park_name)
    else:
        median = load_revenue_median(park_name)
        stdev = load_revenue_stdev(park_name)
    error_level = median-stdev
    warning_level = median-0.3*stdev
    
    
    if metric < error_level:
        return "error"
    elif metric < warning_level:
        return "warning"
    else:
        return "success"
    
def determine_volume_grade(produced_volume, dayahead_volume = None, park_name = None):
    if dayahead_volume: metric = produced_volume-dayahead_volume
    else: metric = produced_volume
    if not park_name: park_name = 'total'

    median = load_diff_production_median(park_name)
    stdev = load_diff_production_std(park_name)
    
    error_level = median-1.6*stdev
    warning_level = median-0.9*stdev
    
    
    if metric < error_level:
        return "error"
    elif metric < warning_level:
        return "warning"
    else:
        return "success"
    
def determine_offset(revenue, dayahead_revenue = None, park_name=None):
    #print(f"\n----\nDetermining offset for {park_name}")
    #print(f"Revenue: {revenue}, dayahead: {dayahead_revenue}")
    
    if get_metric() in ["diff_median", "diff_mean"]:
        metric = revenue-dayahead_revenue
        if(park_name): median = load_revenue_diff_median(park_name)
        else: median = load_revenue_diff_median('total')
    else: 
        metric = revenue
        if(park_name): median = load_revenue_median(park_name)
        else: median = load_revenue_median('total')
    #print(f"metric: {metric}, median: {median}")
    
    if median>0: percentage = metric / median
    else: percentage = metric / 100
    if percentage<1:
        return [f"-{round((1-percentage)*100, 2)}%", metric-median]
    else:
        return [f"+{round((percentage-1)*100, 2)}%", metric-median]