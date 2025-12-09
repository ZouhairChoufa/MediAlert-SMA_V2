from app.services.firebase_service import FirebaseService
from math import radians, sin, cos, sqrt, atan2

class HospitalFirebaseService:
    def __init__(self):
        self.firebase = FirebaseService()
        self.collection = self.firebase.get_collection('hospitals')
    
    def haversine_distance(self, lat1, lon1, lat2, lon2):
        R = 6371
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        return R * c
    
    def get_all_hospitals(self):
        return [doc.to_dict() | {'id': doc.id} for doc in self.collection.stream()]
    
    def find_nearest_hospital(self, patient_lat, patient_lon):
        hospitals = self.get_all_hospitals()
        if not hospitals:
            return None
        
        hospitals_with_distance = []
        for hospital in hospitals:
            distance = self.haversine_distance(
                patient_lat, patient_lon,
                hospital['lat'], hospital['lng']
            )
            hospitals_with_distance.append({
                'hospital': hospital,
                'distance': distance
            })
        
        hospitals_with_distance.sort(key=lambda x: x['distance'])
        nearest = hospitals_with_distance[0]['hospital']
        
        from app.services.ors_service import ORSService
        ors = ORSService()
        route_data = ors.get_route(
            start_coords=[patient_lon, patient_lat],
            end_coords=[nearest['lng'], nearest['lat']]
        )
        
        return {
            'id': nearest.get('id'),
            'name': nearest['name'],
            'service': 'Urgences',
            'distance_km': route_data.get('distance_km', round(hospitals_with_distance[0]['distance'], 2)),
            'eta_minutes': route_data.get('duration_min', 15),
            'coordinates': {'lat': nearest['lat'], 'lng': nearest['lng']},
            'locality': nearest.get('locality', ''),
            'route_geometry': route_data.get('geometry', '')
        }
    
    def add_hospital(self, hospital_data):
        doc_ref = self.collection.document()
        doc_ref.set(hospital_data)
        return doc_ref.id
    
    def update_hospital(self, hospital_id, hospital_data):
        self.collection.document(hospital_id).update(hospital_data)
    
    def delete_hospital(self, hospital_id):
        self.collection.document(hospital_id).delete()
