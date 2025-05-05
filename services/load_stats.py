import pandas as pd

_revenue_stats_df = pd.read_csv("files/revenue_stats.csv").set_index("park")
_price_stats_df = pd.read_csv("files/price_stats.csv").set_index("price_area")
_prod_stats_df = pd.read_csv("files/production_stats.csv").set_index("park")

def normalize_name(name):
    return "maalarberget" if name == "målarberget" else name

def load_revenue_mean(park_name):
    return _revenue_stats_df.loc[normalize_name(park_name), "mean"]

def load_revenue_median(park_name):
    return _revenue_stats_df.loc[normalize_name(park_name), "median"]

def load_revenue_stdev(park_name):
    return _revenue_stats_df.loc[normalize_name(park_name), "stdev"]

def load_revenue_diff_mean(park_name):
    return _revenue_stats_df.loc[normalize_name(park_name), "diff_mean"]

def load_revenue_diff_median(park_name):
    return _revenue_stats_df.loc[normalize_name(park_name), "diff_median"]

def load_revenue_diff_stdev(park_name):
    return _revenue_stats_df.loc[normalize_name(park_name), "diff_stdev"]

def load_spot_median(area):
    return _price_stats_df.loc[area, "spot_median"]

def load_spot_std(area):
    return _price_stats_df.loc[area, "spot_std"]

def load_reg_median(area):
    return _price_stats_df.loc[area, "reg_median"]

def load_reg_std(area):
    return _price_stats_df.loc[area, "reg_std"]

def load_dayahead_production_median(park_name):
    return _prod_stats_df.loc[normalize_name(park_name), "dayahead_median"]

def load_prod_production_median(park_name):
    return _prod_stats_df.loc[normalize_name(park_name), "prod_median"]

def load_diff_production_median(park_name):
    return _prod_stats_df.loc[normalize_name(park_name), "diff_median"]

def load_dayahead_production_std(park_name):
    return _prod_stats_df.loc[normalize_name(park_name), "dayahead_std"]

def load_prod_production_std(park_name):
    return _prod_stats_df.loc[normalize_name(park_name), "prod_std"]

def load_diff_production_std(park_name):
    return _prod_stats_df.loc[normalize_name(park_name), "diff_std"]


