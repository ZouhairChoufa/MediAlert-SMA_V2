from datetime import datetime
from app.services.firebase_service import FirebaseService

class PatientProfile:
    def __init__(self, username, nom_prenom, age, sexe, email, phone='', address='', blood_type='', allergies=None, medical_history=None):
        self.username = username
        self.nom_prenom = nom_prenom
        self.age = age
        self.sexe = sexe
        self.email = email
        self.phone = phone
        self.address = address
        self.blood_type = blood_type
        self.allergies = allergies or []
        self.medical_history = medical_history or []
        self.alerts = []
    
    def add_alert(self, alert_data):
        self.alerts.append(alert_data)
    
    def to_dict(self):
        return {
            'username': self.username,
            'nom_prenom': self.nom_prenom,
            'age': self.age,
            'sexe': self.sexe,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'blood_type': self.blood_type,
            'allergies': self.allergies,
            'medical_history': self.medical_history,
            'alerts': self.alerts
        }
    
    @staticmethod
    def from_dict(data):
        profile = PatientProfile(
            username=data['username'],
            nom_prenom=data['nom_prenom'],
            age=data['age'],
            sexe=data['sexe'],
            email=data['email'],
            phone=data.get('phone', ''),
            address=data.get('address', ''),
            blood_type=data.get('blood_type', ''),
            allergies=data.get('allergies', []),
            medical_history=data.get('medical_history', [])
        )
        profile.alerts = data.get('alerts', [])
        return profile

class PatientStore:
    def __init__(self):
        self.firebase = FirebaseService()
        self.collection = self.firebase.get_collection('patients')
    
    def create_profile(self, username, nom_prenom, age, sexe, email, **kwargs):
        if self.collection.document(username).get().exists:
            return None
        
        profile = PatientProfile(username, nom_prenom, age, sexe, email, **kwargs)
        self.collection.document(username).set(profile.to_dict())
        return profile
    
    def get_profile(self, username):
        doc = self.collection.document(username).get()
        if doc.exists:
            return PatientProfile.from_dict(doc.to_dict())
        return None
    
    def update_profile(self, username, **kwargs):
        doc_ref = self.collection.document(username)
        if not doc_ref.get().exists:
            return None
        
        doc_ref.update(kwargs)
        return self.get_profile(username)
    
    def add_alert_to_profile(self, username, alert_data):
        doc_ref = self.collection.document(username)
        doc = doc_ref.get()
        if not doc.exists:
            return None
        
        profile = PatientProfile.from_dict(doc.to_dict())
        profile.add_alert(alert_data)
        doc_ref.set(profile.to_dict())
        return profile
