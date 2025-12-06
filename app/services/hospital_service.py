import json
import os
from math import radians, sin, cos, sqrt, atan2
from flask import current_app

class HospitalService:
    def __init__(self):
        self.hospitals = None
    
    def load_hospitals(self):
        """Load hospitals from JSON file"""
        if self.hospitals is not None:
            return
        try:
            json_path = os.path.join(current_app.root_path, 'static', 'data', 'hospitals.json')
            with open(json_path, 'r', encoding='utf-8') as f:
                self.hospitals = json.load(f)
        except FileNotFoundError:
            print("Warning: hospitals.json not found")
            self.hospitals = []
    
    def haversine_distance(self, lat1, lon1, lat2, lon2):
        """Calculate Haversine distance between two points in kilometers"""
        R = 6371  # Earth radius in km
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        return R * c
    
    def find_nearest_hospital(self, patient_lat, patient_lon):
        """Find strictly nearest hospital using Haversine and validate with ORS"""
        self.load_hospitals()
        if not self.hospitals:
            return None
        
        # Calculate distances for all hospitals
        hospitals_with_distance = []
        for hospital in self.hospitals:
            distance = self.haversine_distance(
                patient_lat, patient_lon,
                hospital['lat'], hospital['lng']
            )
            hospitals_with_distance.append({
                'hospital': hospital,
                'distance': distance
            })
        
        # Sort by distance and get nearest
        hospitals_with_distance.sort(key=lambda x: x['distance'])
        nearest = hospitals_with_distance[0]['hospital']
        
        # Validate with ORS for real driving route
        from app.services.ors_service import ORSService
        ors = ORSService()
        route_data = ors.get_route(
            start_coords=[patient_lon, patient_lat],
            end_coords=[nearest['lng'], nearest['lat']]
        )
        
        return {
            'id': nearest.get('name', '').replace(' ', '_'),
            'name': nearest['name'],
            'service': 'Urgences',
            'distance_km': route_data.get('distance_km', round(hospitals_with_distance[0]['distance'], 2)),
            'eta_minutes': route_data.get('duration_min', 15),
            'coordinates': {'lat': nearest['lat'], 'lng': nearest['lng']},
            'locality': nearest.get('locality', ''),
            'route_geometry': route_data.get('geometry', '')
        }
    
    def find_nearest(self, lat, lon, required_specialty=None, max_results=5):
        """Find nearest hospitals (legacy method for compatibility)"""
        self.load_hospitals()
        if not self.hospitals:
            return []
        
        hospitals_with_distance = []
        for hospital in self.hospitals:
            distance = self.haversine_distance(lat, lon, hospital['lat'], hospital['lng'])
            hospitals_with_distance.append({
                'name': hospital['name'],
                'latitude': hospital['lat'],
                'longitude': hospital['lng'],
                'distance_km': round(distance, 2),
                'locality': hospital.get('locality', '')
            })
        
        hospitals_with_distance.sort(key=lambda x: x['distance_km'])
        return hospitals_with_distance[:max_results]