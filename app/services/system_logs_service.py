from app.services.firebase_service import FirebaseService
from firebase_admin import firestore

class SystemLogsService:
    def __init__(self):
        self.firebase = FirebaseService()
        self.collection = self.firebase.get_collection('system_logs')
    
    def log_event(self, event_type, message, user=None, metadata=None):
        log_data = {
            'event_type': event_type,
            'message': message,
            'user': user,
            'metadata': metadata or {},
            'timestamp': firestore.SERVER_TIMESTAMP
        }
        self.collection.add(log_data)
    
    def get_recent_logs(self, limit=50):
        docs = self.collection.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit).stream()
        return [doc.to_dict() | {'id': doc.id} for doc in docs]
    
    def get_logs_by_user(self, username, limit=50):
        docs = self.collection.where('user', '==', username).order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit).stream()
        return [doc.to_dict() | {'id': doc.id} for doc in docs]
    
    def get_logs_by_type(self, event_type, limit=50):
        docs = self.collection.where('event_type', '==', event_type).order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit).stream()
        return [doc.to_dict() | {'id': doc.id} for doc in docs]
