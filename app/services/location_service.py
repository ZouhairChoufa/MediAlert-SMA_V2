import requests
from app.config_settings import Config

class LocationService:
    def __init__(self):
        self.api_key = Config.ABSTRACT_API_KEY
        self.base_url = Config.ABSTRACT_API_URL
    
    def get_location_by_ip(self, ip_address=None):
        """Get location from IP address using AbstractAPI"""
        try:
            params = {'api_key': self.api_key}
            if ip_address:
                params['ip_address'] = ip_address
            
            response = requests.get(self.base_url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'latitude': float(data.get('latitude', 0)),
                'longitude': float(data.get('longitude', 0)),
                'city': data.get('city', 'Unknown'),
                'country': data.get('country', 'Unknown'),
                'accuracy': 'ip_based'
            }
        except Exception as e:
            # Fallback to Casablanca coordinates
            return {
                'latitude': 33.5731,
                'longitude': -7.5898,
                'city': 'Casablanca',
                'country': 'Morocco',
                'accuracy': 'fallback',
                'error': str(e)
            }
    
    def validate_coordinates(self, lat, lon):
        """Validate if coordinates are within Morocco bounds"""
        morocco_bounds = {
            'north': 35.9224,
            'south': 27.6626,
            'east': -0.9913,
            'west': -13.1681
        }
        
        return (morocco_bounds['south'] <= lat <= morocco_bounds['north'] and
                morocco_bounds['west'] <= lon <= morocco_bounds['east'])
