import openrouteservice as ors
import polyline
from app.config_settings import Config

class ORSService:
    def __init__(self):
        self.client = ors.Client(key=Config.ORS_API_KEY)
    
    def get_route(self, start_coords, end_coords):
        """
        Calculate route between two points
        Args:
            start_coords: [longitude, latitude]
            end_coords: [longitude, latitude]
        Returns:
            dict: {distance_km, duration_min, geometry}
        """
        try:
            route = self.client.directions(
                coordinates=[start_coords, end_coords],
                profile='driving-car',
                format='geojson',
                geometry_format='polyline'
            )
            
            properties = route['features'][0]['properties']
            geometry = route['features'][0]['geometry']
            
            # Decode polyline for frontend
            decoded_coords = polyline.decode(geometry['coordinates'])
            
            return {
                'distance_km': round(properties['segments'][0]['distance'] / 1000, 2),
                'duration_min': round(properties['segments'][0]['duration'] / 60, 1),
                'geometry': geometry['coordinates'],  # Encoded polyline
                'coordinates': decoded_coords  # Decoded for map display
            }
        except Exception as e:
            # Fallback to straight line calculation
            from geopy.distance import geodesic
            distance = geodesic((start_coords[1], start_coords[0]), 
                              (end_coords[1], end_coords[0])).kilometers
            
            return {
                'distance_km': round(distance, 2),
                'duration_min': round(distance * 2, 1),  # Estimate 30km/h avg
                'geometry': None,
                'coordinates': [start_coords[::-1], end_coords[::-1]],
                'error': str(e)
            }
    
    def get_ambulance_eta(self, ambulance_location, destination):
        """Calculate ETA for ambulance to destination"""
        route_data = self.get_route(ambulance_location, destination)
        return route_data['duration_min']
