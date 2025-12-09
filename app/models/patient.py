from datetime import datetime
import json
import os

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
    def __init__(self, filepath='data/patients.json'):
        self.filepath = filepath
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        if not os.path.exists(self.filepath):
            with open(self.filepath, 'w') as f:
                json.dump({}, f)
    
    def _load_patients(self):
        with open(self.filepath, 'r') as f:
            data = json.load(f)
            return {k: PatientProfile.from_dict(v) for k, v in data.items()}
    
    def _save_patients(self, patients):
        with open(self.filepath, 'w') as f:
            data = {k: v.to_dict() for k, v in patients.items()}
            json.dump(data, f, indent=2)
    
    def create_profile(self, username, nom_prenom, age, sexe, email, **kwargs):
        patients = self._load_patients()
        if username in patients:
            return None
        
        profile = PatientProfile(username, nom_prenom, age, sexe, email, **kwargs)
        patients[username] = profile
        self._save_patients(patients)
        return profile
    
    def get_profile(self, username):
        patients = self._load_patients()
        return patients.get(username)
    
    def update_profile(self, username, **kwargs):
        patients = self._load_patients()
        if username not in patients:
            return None
        
        profile = patients[username]
        for key, value in kwargs.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        
        self._save_patients(patients)
        return profile
    
    def add_alert_to_profile(self, username, alert_data):
        patients = self._load_patients()
        if username not in patients:
            return None
        
        profile = patients[username]
        profile.add_alert(alert_data)
        self._save_patients(patients)
        return profile
