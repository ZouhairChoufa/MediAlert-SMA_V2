#!/usr/bin/env python3
"""Simple test without Unicode characters"""

def test_basic():
    try:
        import flask
        print("[OK] Flask")
        
        import pandas
        print("[OK] Pandas")
        
        import geopy
        print("[OK] Geopy")
        
        import groq
        print("[OK] Groq")
        
        from langchain_groq import ChatGroq
        print("[OK] LangChain Groq")
        
        from app.services.hospital_service import HospitalService
        print("[OK] Hospital Service")
        
        from app.crew.crew_simple import MediAlertCrew
        print("[OK] MediAlert Crew")
        
        from app import create_app
        app = create_app()
        print("[OK] Flask App Created")
        
        print("\n[SUCCESS] All components working!")
        return True
        
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

if __name__ == "__main__":
    test_basic()