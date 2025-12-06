from crewai_tools import BaseTool
from app.services.hospital_service import HospitalService
from app.services.ors_service import ORSService

class HospitalSearchTool(BaseTool):
    name: str = "hospital_search"
    description: str = "Find nearest hospitals with optional specialty filter"
    
    def __init__(self):
        super().__init__()
        self.hospital_service = HospitalService()
    
    def _run(self, latitude: float, longitude: float, specialty: str = None) -> str:
        """Search for nearest hospitals"""
        hospitals = self.hospital_service.find_nearest(
            lat=latitude, 
            lon=longitude, 
            required_specialty=specialty
        )
        return str(hospitals)

class RouteCalculationTool(BaseTool):
    name: str = "route_calculation"
    description: str = "Calculate route between two points with ETA and distance"
    
    def __init__(self):
        super().__init__()
        self.ors_service = ORSService()
    
    def _run(self, start_lat: float, start_lon: float, end_lat: float, end_lon: float) -> str:
        """Calculate route between two coordinates"""
        route_data = self.ors_service.get_route(
            start_coords=[start_lon, start_lat],
            end_coords=[end_lon, end_lat]
        )
        return str(route_data)