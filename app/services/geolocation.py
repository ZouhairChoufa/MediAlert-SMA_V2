import requests
import re
from app.config_settings import Config

class GeolocationService:
    def __init__(self):
        self.abstract_api_key = Config.ABSTRACT_API_KEY
        self.photon_url = "https://photon.komoot.io/api/"
        
        self.nominatim_url_search = "https://nominatim.openstreetmap.org/search"
        self.nominatim_headers = {
            "User-Agent": "MediAlert-Emergency-System/1.0",
            "Accept-Language": "fr" 
        }

        self.morocco_locations = {
            'casablanca': {'lat': 33.5731, 'lng': -7.5898},
            'el jadida': {'lat': 33.2564, 'lng': -8.5106},
            'fes': {'lat': 33.9716, 'lng': -5.0027},
            'marrakech': {'lat': 31.6295, 'lng': -8.0161},
            'tangier': {'lat': 35.7672, 'lng': -5.8102},
            'rabat': {'lat': 34.0209, 'lng': -6.8416},
            'agadir': {'lat': 30.4278, 'lng': -9.5981},
            'oujda': {'lat': 34.6814, 'lng': -1.9097},
        }
    
    def get_ip_location(self, ip_address):
        # ... (Code IP inchangé) ...
        return None
    
    def geocode_address(self, address):
        """Geocode: Photon (Priorité) -> Nominatim (Smart Split) -> Fallback"""
        if not address: return None
        
        address_clean = address.strip()
        print(f"[Geocode] Attempting: '{address_clean}'", flush=True)

        # 1. ESSAI PHOTON (Augmentation du Timeout à 10s)
        try:
            params = {'q': address_clean, 'limit': 1}
            # CORRECTION : Timeout passé de 3 à 10 secondes pour votre connexion
            resp = requests.get(self.photon_url, params=params, timeout=10)
            
            if resp.status_code == 200:
                features = resp.json().get('features', [])
                if features:
                    coords = features[0]['geometry']['coordinates']
                    props = features[0]['properties']
                    print(f"[Geocode] SUCCESS (Photon): {props.get('name')}", flush=True)
                    return {
                        'lat': float(coords[1]),
                        'lng': float(coords[0]),
                        'address': f"{props.get('name', '')}, {props.get('city', '')}",
                        'source': 'photon_api'
                    }
        except Exception as e:
            print(f"[Geocode] Photon API error: {e}", flush=True)

        # 2. ESSAI NOMINATIM (Avec stratégies multiples)
        queries = [address_clean]
        
        # Stratégie A : Enlever le numéro au début (ex: "r318 Av..." -> "Av...")
        cleaned_start = re.sub(r'^\w*\d+\w*\s+', '', address_clean) 
        if cleaned_start != address_clean:
            queries.append(cleaned_start)
            
        # Stratégie B : COUPER A LA VIRGULE (ex: "Gare..., Casa" -> "Gare...")
        # C'est ce qui va sauver votre cas actuel
        if "," in address_clean:
            simple_part = address_clean.split(',')[0].strip()
            if simple_part not in queries:
                queries.append(simple_part)

        for query in queries:
            try:
                # On ignore les requêtes trop courtes pour éviter les faux positifs
                if len(query) < 4: continue 
                
                print(f"[Geocode] Nominatim trying: '{query}'...", flush=True)
                params = {'q': query, 'format': 'json', 'limit': 1}
                resp = requests.get(self.nominatim_url_search, params=params, headers=self.nominatim_headers, timeout=5)
                results = resp.json()
                if results:
                    r = results[0]
                    print(f"[Geocode] SUCCESS (Nominatim via '{query}')", flush=True)
                    return {
                        'lat': float(r['lat']), 'lng': float(r['lon']), 
                        'address': r.get('display_name'), 'source': 'nominatim'
                    }
            except Exception: pass

        # 3. FALLBACK VILLE
        for city, coords in self.morocco_locations.items():
            if city in address_clean.lower():
                return {'lat': coords['lat'], 'lng': coords['lng'], 'address': city, 'source': 'fallback'}
        
        return None

    def merge_all_location_sources(self, gps=None, manual=None, ip=None):
        if manual and (manual.get('address') or (manual.get('lat') and manual.get('lng'))):
            if manual.get('address') and not manual.get('lat'):
                geocoded = self.geocode_address(manual['address'])
                if geocoded: return geocoded
            
            return {
                'lat': float(manual.get('lat') or 0),
                'lng': float(manual.get('lng') or 0),
                'address': manual.get('address'),
                'source': 'manual'
            }
        
        if gps and gps.get('lat'): return gps
        if ip and ip.get('lat'): return ip
        
        return {'lat': 33.5731, 'lng': -7.5898, 'address': 'Casablanca', 'source': 'default'}