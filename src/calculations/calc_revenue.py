from src.read_data import read_forecast_data, read_price
from services.constants import get_date, price_areas

def calc_revenue(parkname, target_date=None):
    if not target_date: target_date = get_date()
    parkdata = read_forecast_data(parkname, target_date)
    spotprice = read_price('spot', price_areas()[parkname])['value'].values
    regprice = read_price('reg', price_areas()[parkname])['value'].values
    
    sold_volume = parkdata.get('datasets')[0].get('data')
    produced_volume = parkdata.get('datasets')[1].get('data')
    result = [sold_volume[i]*spotprice[i]-(sold_volume[i]-produced_volume[i])*regprice[i] for i in range(len(sold_volume))]
    
    return sum(result)