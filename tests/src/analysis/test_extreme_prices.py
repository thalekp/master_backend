import pytest
from src.analysis.extreme_prices import find_extreme_prices
from services.constants import get_date
from datetime import date

def test_price_abnormality_se3():
    target_date = date(2025, 1, 26)
    extreme_reg_prices = find_extreme_prices('SE3', target_date)
    assert len(extreme_reg_prices)==0
    target_date = date(2025, 2, 19)
    extreme_reg_prices = find_extreme_prices('SE3', target_date)
    assert len(extreme_reg_prices)>0

def test_price_abnormality_no3():
    target_date = date(2025, 1, 9)
    extreme_reg_prices = find_extreme_prices('NO3', target_date)
    assert len(extreme_reg_prices)==0
    target_date = date(2025, 2, 4)
    extreme_reg_prices = find_extreme_prices('NO3', target_date)
    assert len(extreme_reg_prices)==0
    
def test_price_abnormality_se2():
    target_date = date(2025, 1, 7)
    extreme_reg_prices = find_extreme_prices('SE2', target_date)
    assert len(extreme_reg_prices)==0
    target_date = date(2025, 1, 21)
    extreme_reg_prices = find_extreme_prices('SE2', target_date)
    assert len(extreme_reg_prices)==0
    target_date = date(2025, 3, 4)
    extreme_reg_prices = find_extreme_prices('SE2', target_date)
    assert len(extreme_reg_prices)>0
    