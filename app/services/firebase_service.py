import firebase_admin
from firebase_admin import credentials, firestore
import os

class FirebaseService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        if not firebase_admin._apps:
            cred_path = os.path.join('config', 'firebase-credentials.json')
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        self.db = firestore.client()
    
    def get_collection(self, collection_name):
        return self.db.collection(collection_name)
