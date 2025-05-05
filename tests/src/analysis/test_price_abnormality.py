import pytest
from src.analysis.price_abnormality import price_abnormality
from services.constants import get_date
from datetime import date

def test_price_abnormality_se3():
    target_date = date(2025, 1, 26)
    imbalance = price_abnormality('SE3', target_date)
    assert imbalance>1
    target_date = date(2025, 2, 19)
    imbalance = price_abnormality('SE3', target_date)
    assert imbalance>1

def test_price_abnormality_no3():
    target_date = date(2025, 1, 9)
    imbalance = price_abnormality('NO3', target_date)
    assert imbalance>1
    target_date = date(2025, 2, 4)
    imbalance = price_abnormality('NO3', target_date)
    assert imbalance>1
    
def test_price_abnormality_se2():
    target_date = date(2025, 1, 7)
    imbalance = price_abnormality('SE2', target_date)
    assert not imbalance>1
    target_date = date(2025, 1, 21)
    imbalance = price_abnormality('SE2', target_date)
    assert not imbalance>1
    target_date = date(2025, 3, 4)
    imbalance = price_abnormality('SE2', target_date)
    assert imbalance>1
    