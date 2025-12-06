import requests
from app.config import Config

class GeolocationService:
    def __init__(self):
        self.abstract_api_key = Config.ABSTRACT_API_KEY
    
    def get_ip_location(self, ip_address):
        """Get location from IP using AbstractAPI"""
        try:
            url = f"https://ipgeolocation.abstractapi.com/v1/?api_key={self.abstract_api_key}&ip_address={ip_address}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return {
                    'lat': float(data.get('latitude', 0)),
                    'lng': float(data.get('longitude', 0)),
                    'city': data.get('city', ''),
                    'country': data.get('country', ''),
                    'source': 'ip',
                    'accuracy': 'low'
                }
        except Exception as e:
            print(f"IP geolocation failed: {e}")
        return None
    
    def merge_all_location_sources(self, gps=None, manual=None, ip=None):
        """Merge location sources with priority: GPS > Manual > IP"""
        # Priority 1: GPS with high accuracy
        if gps and gps.get('accuracy', 999) < 100:
            return {
                'lat': gps['lat'],
                'lng': gps['lng'],
                'address': gps.get('address', ''),
                'source': 'gps',
                'confidence': 'high'
            }
        
        # Priority 2: Manual input
        if manual and manual.get('address'):
            return {
                'lat': manual.get('lat', 0),
                'lng': manual.get('lng', 0),
                'address': manual['address'],
                'source': 'manual',
                'confidence': 'medium'
            }
        
        # Priority 3: IP fallback
        if ip:
            return {
                'lat': ip['lat'],
                'lng': ip['lng'],
                'address': f"{ip.get('city', '')}, {ip.get('country', '')}",
                'source': 'ip',
                'confidence': 'low'
            }
        
        # Default fallback (Casablanca)
        return {
            'lat': 33.5731,
            'lng': -7.5898,
            'address': 'Casablanca, Morocco',
            'source': 'default',
            'confidence': 'low'
        }
