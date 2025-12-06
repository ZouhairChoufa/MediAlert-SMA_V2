import json
import os
from math import radians, sin, cos, sqrt, atan2
from flask import current_app
from app.services.ors_service import ORSService

class SmartDispatchEngine:
    def __init__(self):
        try:
            self.ors_service = ORSService()
        except Exception as e:
            print(f"Warning: ORS service unavailable: {e}")
            self.ors_service = None
        self.hospitals = None
    
    def load_hospitals(self):
        """Load hospitals from JSON"""
        if self.hospitals is not None:
            return
        try:
            json_path = os.path.join(current_app.root_path, 'static', 'data', 'hospitals.json')
            with open(json_path, 'r', encoding='utf-8') as f:
                self.hospitals = json.load(f)
        except Exception as e:
            print(f"Failed to load hospitals: {e}")
            self.hospitals = []
    
    def haversine_distance(self, lat1, lon1, lat2, lon2):
        """Calculate Haversine distance in km"""
        R = 6371
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        return R * c
    
    def calculate_weighted_score(self, distance_km, travel_time_min, emergency_level):
        """Calculate hospital priority score (lower is better)"""
        weights = {'distance': 0.4, 'time': 0.5, 'emergency': 0.1}
        emergency_factor = 1.0 if emergency_level >= 3 else 0.8
        return (distance_km * weights['distance'] + 
                travel_time_min * weights['time']) * emergency_factor
    
    def dispatch_ambulance(self, patient_lat, patient_lon, emergency_level=2, ambulance_coords=None):
        """Main dispatch workflow"""
        self.load_hospitals()
        if not self.hospitals:
            return None
        
        # Default ambulance location (can be dynamic)
        if not ambulance_coords:
            ambulance_coords = [patient_lat, patient_lon]
        
        # Step 1: Calculate distances to all hospitals
        hospitals_ranked = []
        for hospital in self.hospitals:
            distance = self.haversine_distance(
                patient_lat, patient_lon,
                hospital['lat'], hospital['lng']
            )
            hospitals_ranked.append({
                'hospital': hospital,
                'distance_km': distance
            })
        
        # Step 2: Sort by distance
        hospitals_ranked.sort(key=lambda x: x['distance_km'])
        
        # Step 3: Get optimal hospital (nearest)
        optimal = hospitals_ranked[0]
        hospital = optimal['hospital']
        
        # Step 4: Calculate full mission trajectory
        if self.ors_service:
            try:
                # Ambulance -> Patient
                leg1 = self.ors_service.get_route(
                    start_coords=[ambulance_coords[1], ambulance_coords[0]],
                    end_coords=[patient_lon, patient_lat]
                )
                
                # Patient -> Hospital
                leg2 = self.ors_service.get_route(
                    start_coords=[patient_lon, patient_lat],
                    end_coords=[hospital['lng'], hospital['lat']]
                )
                
                total_distance = leg1.get('distance_km', 0) + leg2.get('distance_km', 0)
                total_time = leg1.get('duration_min', 0) + leg2.get('duration_min', 0)
                full_geometry = leg2.get('geometry', '')
                
            except Exception as e:
                print(f"ORS routing failed: {e}")
                total_distance = optimal['distance_km']
                total_time = int(total_distance * 3)
                full_geometry = ''
        else:
            # Fallback without ORS
            total_distance = optimal['distance_km']
            total_time = int(total_distance * 3)
            full_geometry = ''
        
        return {
            'hospital': {
                'id': hospital['name'].replace(' ', '_'),
                'name': hospital['name'],
                'locality': hospital.get('locality', ''),
                'coordinates': {'lat': hospital['lat'], 'lng': hospital['lng']}
            },
            'mission': {
                'total_distance_km': round(total_distance, 2),
                'total_eta_minutes': int(total_time),
                'ambulance_to_patient_min': leg1.get('duration_min', 5) if 'leg1' in locals() else 5,
                'patient_to_hospital_min': leg2.get('duration_min', 10) if 'leg2' in locals() else 10,
                'trajectory_geometry': full_geometry,
                'emergency_level': emergency_level
            },
            'route_coordinates': [
                [ambulance_coords[0], ambulance_coords[1]],
                [patient_lat, patient_lon],
                [hospital['lat'], hospital['lng']]
            ]
        }
