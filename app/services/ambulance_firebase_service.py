from app.services.firebase_service import FirebaseService
from firebase_admin import firestore
import json
import os

class AmbulanceFirebaseService:
    def __init__(self):
        self.firebase = FirebaseService()
        self.collection = self.firebase.get_collection('ambulances')
    
    def get_all_ambulances(self):
        """Récupère toutes les ambulances (Firebase ou JSON local)"""
        try:
            docs = list(self.collection.stream())
            if docs:
                return [doc.to_dict() | {'id': doc.id} for doc in docs]
        except Exception as e:
            print(f"[AmbulanceService] Erreur lecture Firestore: {e}", flush=True)

        # Fallback JSON
        try:
            # On remonte de 2 dossiers pour trouver static/data
            json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'data', 'ambulances.json')
            with open(json_path, 'r', encoding='utf-8') as f:
                ambulances = json.load(f)
                return ambulances
        except FileNotFoundError:
            print("[AmbulanceService] Attention: ambulances.json introuvable", flush=True)
            return []
        except Exception as e:
            print(f"[AmbulanceService] Erreur lecture JSON: {e}", flush=True)
            return []
    
    def get_available_ambulances(self):
        """Récupère uniquement les ambulances libres"""
        # 1. Essai Firestore avec filtre
        try:
            docs = list(self.collection.where('status', '==', 'available').stream())
            if docs:
                return [doc.to_dict() | {'id': doc.id} for doc in docs]
        except Exception:
            pass # Si Firestore échoue, on continue vers le fallback

        # 2. Fallback sur get_all_ambulances + filtre Python
        all_ambs = self.get_all_ambulances()
        return [a for a in all_ambs if a.get('status') == 'available']

    def get_available_by_level(self, emergency_level):
        """
        NOUVELLE MÉTHODE : Sélectionne les ambulances selon la gravité.
        - Niveau 3 (Critique) : Cherche Type A (SMUR) en priorité.
        - Niveau 1-2 : Prend tout ce qui est disponible.
        """
        available = self.get_available_ambulances()
        if not available:
            return []
        
        try:
            level = int(emergency_level)
            
            # Si Urgence Critique (3+), on filtre pour chercher le "Type A" ou "SMUR"
            if level >= 3:
                advanced_units = []
                for amb in available:
                    name = amb.get('name', '').upper()
                    type_amb = amb.get('type', '').upper()
                    
                    if 'SMUR' in name or 'TYPE A' in type_amb or 'REANIMATION' in name:
                        advanced_units.append(amb)
                
                # Si on a trouvé des unités d'élite, on ne renvoie qu'elles
                if advanced_units:
                    print(f"[AmbulanceService] Urgence Niveau {level} -> {len(advanced_units)} ambulances SMUR trouvées.", flush=True)
                    return advanced_units
                
                print(f"[AmbulanceService] Urgence Niveau {level} mais pas de SMUR dispo -> Envoi ambulance standard.", flush=True)

        except Exception as e:
            print(f"[AmbulanceService] Erreur filtre niveau: {e}", flush=True)

        # Par défaut (ou si niveau faible), on retourne toutes les disponibles
        return available
    
    def get_ambulance(self, ambulance_id):
        try:
            doc = self.collection.document(ambulance_id).get()
            if doc.exists:
                return doc.to_dict() | {'id': doc.id}
        except Exception:
            pass
        # Recherche dans le fallback local si non trouvé
        for amb in self.get_all_ambulances():
            if amb.get('id') == ambulance_id:
                return amb
        return None
    
    def add_ambulance(self, ambulance_data):
        doc_ref = self.collection.document()
        ambulance_data['created_at'] = firestore.SERVER_TIMESTAMP
        ambulance_data['status'] = ambulance_data.get('status', 'available')
        doc_ref.set(ambulance_data)
        return doc_ref.id
    
    def update_ambulance_status(self, ambulance_id, status):
        try:
            self.collection.document(ambulance_id).update({
                'status': status,
                'updated_at': firestore.SERVER_TIMESTAMP
            })
        except Exception:
            pass 
    
    def update_ambulance_location(self, ambulance_id, lat, lng):
        try:
            self.collection.document(ambulance_id).update({
                'current_location': {'lat': lat, 'lng': lng},
                'updated_at': firestore.SERVER_TIMESTAMP
            })
        except Exception:
            pass

    def assign_ambulance(self, ambulance_id, alert_id):
        try:
            self.collection.document(ambulance_id).update({
                'status': 'assigned',
                'current_alert_id': alert_id,
                'updated_at': firestore.SERVER_TIMESTAMP
            })
        except Exception:
            pass

    def delete_ambulance(self, ambulance_id):
        self.collection.document(ambulance_id).delete()