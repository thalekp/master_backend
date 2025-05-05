import json

def load_revenue_mean(park_name):
    with open("files/revenue_stats.json") as f:
        means = json.load(f)
    if park_name == 'målarberget': return means.get('maalarberget').get('mean')
    else: return means.get(park_name).get('mean')
    
def load_revenue_median(park_name):
    with open("files/revenue_stats.json") as f:
        means = json.load(f)
    if park_name == 'målarberget': return means.get('maalarberget').get('median')
    else: return means.get(park_name).get('median')

def load_revenue_stdev(park_name):
    with open("files/revenue_stats.json") as f:
        means = json.load(f)
    if park_name == 'målarberget': return means.get('maalarberget').get('stdev')
    else: return means.get(park_name).get('stdev')
    
def load_revenue_diff_mean(park_name):
    with open("files/revenue_stats.json") as f:
        means = json.load(f)
    if park_name == 'målarberget': return means.get('maalarberget').get('mean')
    else: return means.get(park_name).get('mean')
    
def load_revenue_diff_median(park_name):
    with open("files/revenue_stats.json") as f:
        means = json.load(f)
    if park_name == 'målarberget': return means.get('maalarberget').get('diff_median')
    else: return means.get(park_name).get('diff_median')
    
def load_revenue_diff_stdev(park_name):
    with open("files/revenue_stats.json") as f:
        means = json.load(f)
    if park_name == 'målarberget': return means.get('maalarberget').get('diff_stdev')
    else: return means.get(park_name).get('diff_stdev')
    
    

