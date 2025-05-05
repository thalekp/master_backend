from services.load_stats import load_revenue_median, load_revenue_diff_median, load_revenue_stdev, load_revenue_diff_stdev
from services.config import get_metric

def determine_revenue_grade(revenue,dayahead_revenue = None, park_name = None):
    #print(f"\n---\ndetermining revenue status for: {park_name}")
    #print(f"Revenue: {revenue}, dayahead: {dayahead_revenue}")

    if dayahead_revenue: metric = revenue-dayahead_revenue
    else: metric = revenue
    if not park_name: park_name = 'total'

    if get_metric() in ["diff_median", "diff_mean"]:
        median = load_revenue_diff_median(park_name)
        stdev = load_revenue_diff_stdev(park_name)
    else:
        median = load_revenue_median(park_name)
        stdev = load_revenue_stdev(park_name)
    error_level = median-5*stdev
    warning_level = median-2*stdev
        
    
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