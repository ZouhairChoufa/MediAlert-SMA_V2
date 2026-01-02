import requests
import json
# Importation de votre configuration pour lire le .env
from app.config_settings import Config 

class ORSService:
    def __init__(self):
        # ✅ RÉCUPÉRATION AUTOMATIQUE DEPUIS LE .ENV
        # Plus besoin de copier-coller la clé ici
        self.api_key = Config.ORS_API_KEY 
        
        self.base_url = "https://api.openrouteservice.org/v2/directions/driving-car"

    def get_route(self, start_coords, end_coords):
        """
        Calcule un itinéraire routier précis en utilisant la clé du .env
        """
        # Vérification de sécurité
        if not self.api_key:
            print("[ORS] ERREUR CRITIQUE : Clé API introuvable dans Config.ORS_API_KEY")
            return self._fallback_route(start_coords, end_coords)

        headers = {
            'Authorization': self.api_key,
            'Content-Type': 'application/json; charset=utf-8'
        }
        
        # OpenRouteService attend [Longitude, Latitude]
        body = {
            "coordinates": [start_coords, end_coords],
            "instructions": "false",
            "preference": "fastest"
        }
        
        try:
            # Appel API via requests (plus stable que la librairie officielle)
            response = requests.post(f"{self.base_url}/geojson", json=body, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extraction
                feature = data['features'][0]
                geometry = feature['geometry']['coordinates'] # [[lon, lat], ...]
                props = feature['properties']['summary']
                
                # Conversion pour Leaflet [Lat, Lon]
                path_leaflet = [[coord[1], coord[0]] for coord in geometry]
                
                return {
                    'coordinates': path_leaflet, 
                    'distance_km': round(props['distance'] / 1000, 2),
                    'duration_min': round(props['duration'] / 60, 0)
                }
            else:
                print(f"[ORS Error] API a répondu : {response.status_code} - {response.text}")
                return self._fallback_route(start_coords, end_coords)
                
        except Exception as e:
            print(f"[ORS Exception] {e}")
            return self._fallback_route(start_coords, end_coords)

    def _fallback_route(self, start, end):
        """Mode secours : Ligne droite si l'API échoue"""
        print("[ORS] Utilisation du mode secours (Ligne droite)")
        return {
            'coordinates': [[start[1], start[0]], [end[1], end[0]]],
            'distance_km': 0,
            'duration_min': 5
        }