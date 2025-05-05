import pytest
from src.analysis.unforeseen_event import unforeseen_event
from services.constants import get_date
from datetime import date

def test_price_abnormality_maalarberget():
    target_date = date(2025, 1, 26)
    strange_hours = unforeseen_event('maalarberget', target_date)
    assert len(strange_hours)<3
    target_date = date(2025, 2, 19)
    strange_hours = unforeseen_event('maalarberget', target_date)
    assert len(strange_hours)<3

def test_price_abnormality_roan():
    target_date = date(2025, 1, 9)
    strange_hours = unforeseen_event('roan', target_date)
    assert len(strange_hours)<3
    target_date = date(2025, 1, 23)
    strange_hours = unforeseen_event('roan', target_date)
    assert not len(strange_hours)<3
    target_date = date(2025, 2, 4)
    strange_hours = unforeseen_event('roan', target_date)
    assert len(strange_hours)>0
    
def test_price_abnormality_klevberget():
    target_date = date(2025, 1, 7)
    strange_hours = unforeseen_event('klevberget', target_date)
    assert len(strange_hours)>0
    target_date = date(2025, 1, 21)
    strange_hours = unforeseen_event('klevberget', target_date)
    assert len(strange_hours)>0
    target_date = date(2025, 1, 23)
    strange_hours = unforeseen_event('klevberget', target_date)
    assert len(strange_hours)>0
    target_date = date(2025, 1, 24)
    strange_hours = unforeseen_event('klevberget', target_date)
    assert len(strange_hours)>0
    target_date = date(2025, 1, 25)
    strange_hours = unforeseen_event('klevberget', target_date)
    assert len(strange_hours)>0
    target_date = date(2025, 1, 30)
    strange_hours = unforeseen_event('klevberget', target_date)
    assert len(strange_hours)>0
    target_date = date(2025, 1, 31)
    strange_hours = unforeseen_event('klevberget', target_date)
    assert len(strange_hours)>0
    target_date = date(2025, 2, 1)
    strange_hours = unforeseen_event('klevberget', target_date)
    assert len(strange_hours)>0
    target_date = date(2025, 2, 2)
    strange_hours = unforeseen_event('klevberget', target_date)
    assert len(strange_hours)>0
    target_date = date(2025, 2, 3)
    strange_hours = unforeseen_event('klevberget', target_date)
    assert len(strange_hours)>0
    target_date = date(2025, 2, 4)
    strange_hours = unforeseen_event('klevberget', target_date)
    assert len(strange_hours)>0
    target_date = date(2025, 2, 5)
    strange_hours = unforeseen_event('klevberget', target_date)
    assert len(strange_hours)>0
    """target_date = date(2025, 3, 4)
    extreme_reg_prices = unforeseen_event('klevberget', target_date)
    assert len(extreme_reg_prices)<3"""
    