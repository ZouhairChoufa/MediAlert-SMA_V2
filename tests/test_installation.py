#!/usr/bin/env python3
"""
Test script to verify MediAlert Pro v2.0 installation
"""

def test_imports():
    """Test all critical imports"""
    print("Testing imports...")
    
    try:
        import flask
        print("[OK] Flask imported successfully")
    except ImportError as e:
        print(f"[ERROR] Flask import failed: {e}")
        return False
    
    try:
        import pandas
        print("✓ Pandas imported successfully")
    except ImportError as e:
        print(f"✗ Pandas import failed: {e}")
        return False
    
    try:
        import geopy
        print("✓ Geopy imported successfully")
    except ImportError as e:
        print(f"✗ Geopy import failed: {e}")
        return False
    
    try:
        import openrouteservice
        print("✓ OpenRouteService imported successfully")
    except ImportError as e:
        print(f"✗ OpenRouteService import failed: {e}")
        return False
    
    try:
        from groq import Groq
        print("✓ Groq imported successfully")
    except ImportError as e:
        print(f"✗ Groq import failed: {e}")
        return False
    
    try:
        from langchain_groq import ChatGroq
        print("✓ LangChain Groq imported successfully")
    except ImportError as e:
        print(f"✗ LangChain Groq import failed: {e}")
        return False
    
    return True

def test_services():
    """Test service initialization"""
    print("\nTesting services...")
    
    try:
        from app.services.hospital_service import HospitalService
        hospital_service = HospitalService()
        print("✓ Hospital service initialized")
    except Exception as e:
        print(f"✗ Hospital service failed: {e}")
        return False
    
    try:
        from app.services.location_service import LocationService
        location_service = LocationService()
        print("✓ Location service initialized")
    except Exception as e:
        print(f"✗ Location service failed: {e}")
        return False
    
    return True

def test_crew():
    """Test crew initialization"""
    print("\nTesting crew...")
    
    try:
        from app.crew.crew_simple import MediAlertCrew
        print("✓ MediAlert crew imported successfully")
        
        # Note: Don't initialize without API keys
        print("✓ Crew ready for initialization (API keys required)")
    except Exception as e:
        print(f"✗ Crew initialization failed: {e}")
        return False
    
    return True

def test_flask_app():
    """Test Flask app creation"""
    print("\nTesting Flask app...")
    
    try:
        from app import create_app
        app = create_app()
        print("✓ Flask app created successfully")
        print(f"✓ App name: {app.name}")
        return True
    except Exception as e:
        print(f"✗ Flask app creation failed: {e}")
        return False

def main():
    """Run all tests"""
    print("MediAlert Pro v2.0 Installation Test")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Services Test", test_services),
        ("Crew Test", test_crew),
        ("Flask App Test", test_flask_app)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n[TEST] {test_name}")
        print("-" * 30)
        if test_func():
            passed += 1
            print(f"[PASS] {test_name} PASSED")
        else:
            print(f"[FAIL] {test_name} FAILED")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("SUCCESS: All tests passed! MediAlert Pro v2.0 is ready to run.")
        print("\nNext steps:")
        print("1. Add your API keys to .env file")
        print("2. Set up Firebase credentials")
        print("3. Run: python run.py")
    else:
        print("WARNING: Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    main()