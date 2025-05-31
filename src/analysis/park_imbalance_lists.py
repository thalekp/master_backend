from src.read_data import read_price, read_intraday_volumes, read_forecast_data
from services.constants import price_areas


def imbalance_volume(park_name, target_date=None):
    price_area = price_areas().get(park_name)
    dayahead, prod = read_forecast_data(park_name, json = False)
    intraday_buy_volume, intraday_sell_volume = read_intraday_volumes(price_area, json = False)
    return [d+isv-p-ibv for p,d, ibv, isv in zip(prod, dayahead, intraday_buy_volume, intraday_sell_volume)]


def dayahead_earning(park_name, target_date = None):
    price_area = price_areas().get(park_name)
    dayahead, prod = read_forecast_data(park_name, json = False)
    spot = read_price('spot', price_area).value.values.tolist()
    dayahead_earnings = [d*s for d, s in zip(dayahead, spot)]
    return dayahead_earnings

def actual_earning(park_name, target_date = None):
    price_area = price_areas().get(park_name)
    dayahead, prod = read_forecast_data(park_name, json = False)
    park_imbalance_volume = imbalance_volume(park_name, target_date)
    intraday_buy_volume, intraday_sell_volume = read_intraday_volumes(price_area, json = False)
    spot_price = read_price('spot', price_area, target_date).value.values.tolist()
    reg_price = read_price('reg', price_area, target_date).value.values.tolist()
    intraday_buy = read_price('intraday_VWAP_buy', price_area, target_date)
    intraday_sell = read_price('intraday_VWAP_sell', price_area, target_date)
    print(intraday_buy)
    dayahead_earnings = [d*s for d, s in zip(dayahead, spot_price)]
    actual_earnings = [de+idsv*idsp-(iv*r+idbv*idbp) for de, iv, r, idbv, idsv, idbp, idsp in zip(dayahead_earnings, park_imbalance_volume, reg_price, intraday_buy_volume, intraday_sell_volume, intraday_buy, intraday_sell)]
    return actual_earnings
    