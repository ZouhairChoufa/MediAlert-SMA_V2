from crewai.tools import tool

@tool("Hospital Search")
def HospitalSearchTool(lat: float, lng: float, specialty: str) -> str:
    """Search nearest hospital with specific specialty and available beds"""
    from app.services.hospital_firebase_service import HospitalFirebaseService
    hospital_service = HospitalFirebaseService()
    hospitals = hospital_service.find_nearest_with_specialty(lat, lng, specialty)
    return str(hospitals[:3])

@tool("Route Calculator")
def RouteCalculationTool(start_lat: float, start_lng: float, end_lat: float, end_lng: float) -> str:
    """Calculate optimal route with real-time traffic and ETA"""
    from app.services.ors_service import ORSService
    ors = ORSService()
    route = ors.get_route(start_lat, start_lng, end_lat, end_lng)
    return f"Distance: {route['distance']}km, ETA: {route['duration']}min"

@tool("Ambulance Tracker")
def AmbulanceTrackerTool(emergency_level: int) -> str:
    """Find nearest available ambulance by type (emergency_level: 1-5)"""
    from app.services.ambulance_firebase_service import AmbulanceFirebaseService
    ambulance_service = AmbulanceFirebaseService()
    ambulances = ambulance_service.get_available_by_level(emergency_level)
    return str(ambulances[:2])
