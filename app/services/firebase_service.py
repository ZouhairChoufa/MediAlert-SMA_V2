import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import threading
from app.config import Config

class FirebaseService:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            if not firebase_admin._apps:
                cred = credentials.Certificate(Config.FIREBASE_CREDENTIALS_PATH)
                firebase_admin.initialize_app(cred)
            self.db = firestore.client()
            self._initialized = True
    
    def create_alert(self, data):
        """Create new emergency alert"""
        alert_data = {
            **data,
            'created_at': datetime.utcnow(),
            'status': 'pending',
            'crew_logs': []
        }
        doc_ref = self.db.collection('alerts').add(alert_data)
        return doc_ref[1].id
    
    def update_alert_status(self, alert_id, status, logs=None):
        """Update alert status and logs"""
        update_data = {
            'status': status,
            'updated_at': datetime.utcnow()
        }
        if logs:
            update_data['crew_logs'] = logs
        
        self.db.collection('alerts').document(alert_id).update(update_data)
    
    def get_alert(self, alert_id):
        """Get alert by ID"""
        doc = self.db.collection('alerts').document(alert_id).get()
        return doc.to_dict() if doc.exists else None
    
    def stream_alert_status(self, alert_id, callback):
        """Stream real-time updates for alert"""
        def on_snapshot(doc_snapshot, changes, read_time):
            for doc in doc_snapshot:
                callback(doc.to_dict())
        
        return self.db.collection('alerts').document(alert_id).on_snapshot(on_snapshot)