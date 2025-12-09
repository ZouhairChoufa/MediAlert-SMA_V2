from app.services.firebase_service import FirebaseService
from firebase_admin import firestore

class AmbulanceFirebaseService:
    def __init__(self):
        self.firebase = FirebaseService()
        self.collection = self.firebase.get_collection('ambulances')
    
    def get_all_ambulances(self):
        return [doc.to_dict() | {'id': doc.id} for doc in self.collection.stream()]
    
    def get_available_ambulances(self):
        docs = self.collection.where('status', '==', 'available').stream()
        return [doc.to_dict() | {'id': doc.id} for doc in docs]
    
    def get_ambulance(self, ambulance_id):
        doc = self.collection.document(ambulance_id).get()
        if doc.exists:
            return doc.to_dict() | {'id': doc.id}
        return None
    
    def add_ambulance(self, ambulance_data):
        doc_ref = self.collection.document()
        ambulance_data['created_at'] = firestore.SERVER_TIMESTAMP
        ambulance_data['status'] = ambulance_data.get('status', 'available')
        doc_ref.set(ambulance_data)
        return doc_ref.id
    
    def update_ambulance_status(self, ambulance_id, status):
        self.collection.document(ambulance_id).update({
            'status': status,
            'updated_at': firestore.SERVER_TIMESTAMP
        })
    
    def update_ambulance_location(self, ambulance_id, lat, lng):
        self.collection.document(ambulance_id).update({
            'current_location': {'lat': lat, 'lng': lng},
            'updated_at': firestore.SERVER_TIMESTAMP
        })
    
    def assign_ambulance(self, ambulance_id, alert_id):
        self.collection.document(ambulance_id).update({
            'status': 'assigned',
            'current_alert_id': alert_id,
            'updated_at': firestore.SERVER_TIMESTAMP
        })
    
    def delete_ambulance(self, ambulance_id):
        self.collection.document(ambulance_id).delete()
