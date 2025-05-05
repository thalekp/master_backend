import pytest
from src.analysis.volume_abnormality import volume_abnormality
from services.constants import get_date
from datetime import date

def test_volume_abnormality_maalarberget():
    target_date = date(2025, 1, 26)
    imbalance = volume_abnormality('maalarberget', target_date)
    assert imbalance<-1

def test_volume_abnormality_roan():
    target_date = date(2025, 1, 9)
    imbalance = volume_abnormality('roan', target_date)
    assert imbalance<-1
    target_date = date(2025, 2, 4)
    imbalance = volume_abnormality('roan', target_date)
    assert imbalance<-1
    
def test_volume_abnormality_klevberget():
    target_date = date(2025, 1, 7)
    imbalance = volume_abnormality('klevberget', target_date)
    assert imbalance<-1
    target_date = date(2025, 1, 21)
    imbalance = volume_abnormality('klevberget', target_date)
    assert imbalance<-1
    target_date = date(2025, 3, 4)
    imbalance = volume_abnormality('klevberget', target_date)
    assert not imbalance<-1
    