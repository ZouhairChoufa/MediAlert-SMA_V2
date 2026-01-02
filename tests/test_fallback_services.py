import pytest
from app.services.hospital_firebase_service import HospitalFirebaseService
from app.services.ambulance_firebase_service import AmbulanceFirebaseService


def test_hospital_fallback_loads_static():
    hs = HospitalFirebaseService()
    hospitals = hs.get_all_hospitals()
    assert isinstance(hospitals, list)
    assert len(hospitals) > 0


def test_ambulance_fallback_loads_static():
    a = AmbulanceFirebaseService()
    ambulances = a.get_all_ambulances()
    assert isinstance(ambulances, list)
    assert len(ambulances) > 0
    available = a.get_available_ambulances()
    assert isinstance(available, list)