from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from src.component_data.generate_graphs import get_graph
from src.calculations.calc_revenue import calc_revenue
from src.calculations.calc_dayahead_revenue import calc_dayahead_revenue
from src.analysis.determine_status import determine_revenue_grade, determine_offset
from src.component_data.park_report import park_report
from day_report import get_day_report
from services.constants import get_date
from services.parks_list import get_all_parks
from src.component_data.dashboard_data import generate_dashboard_data
from src.component_data.park_cards import generate_park_cards
from src.read_data import read_forecast_data
from datetime import datetime
app = FastAPI()



app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/parkreport/{parkname}")
def get_park_forecast(parkname:str):
    response =  park_report(parkname)
    generate_park_cards(parkname)
    return response
    
@app.get("/api/dayahead/{parkname}")
def get_forecast(parkname:str):
    return get_graph(parkname)
    
@app.get("/api/dashboard_graph")
def get_forecast():
    result = get_graph()
    return result

@app.get("/api/date")
def api_get_date():
    df = pd.read_csv(f"aneo_data/roan_forecasts.csv")
    dayahead = df[df["forecast"] == "dayahead"].copy()
    dayahead["time"] = pd.to_datetime(dayahead["time"])
    all_dates = sorted(dayahead["time"].dt.date.unique(), reverse=True)
    date_strings = [d.strftime("%Y-%m-%d") for d in all_dates][2:]
    date = get_date()
    return {
        "dates": date_strings,
        "date": date
    }

@app.get("/api/set_date")
def api_set_date(date:str):
    stats_df = pd.DataFrame({"date": [date]})
    stats_df.to_csv("files/date.csv", index=False)
    return {
        "response":"success"
    }
    
@app.get("/api/dayreport")
def get_dayreport():
    return {
        "report": get_day_report()
    }

@app.get("/api/dashboard_cards")
def get_dashboard_data():
    return generate_dashboard_data()
