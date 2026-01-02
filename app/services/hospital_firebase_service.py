from app.services.firebase_service import FirebaseService
from math import radians, sin, cos, sqrt, atan2
import json
import os

class HospitalFirebaseService:
    def __init__(self):
        self.firebase = FirebaseService()
        self.collection = self.firebase.get_collection('hospitals')
    
    def haversine_distance(self, lat1, lon1, lat2, lon2):
        """Calcule la distance à vol d'oiseau en km"""
        R = 6371  # Rayon de la Terre
        try:
            lat1, lon1, lat2, lon2 = map(radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            return R * c
        except Exception:
            return 9999.0 # Valeur par défaut en cas d'erreur de coordonnées
    
    def get_all_hospitals(self):
        """Récupère les hôpitaux depuis Firebase ou le fichier JSON local"""
        # 1. Essai Firebase
        try:
            docs = list(self.collection.stream())
            if docs:
                return [doc.to_dict() | {'id': doc.id} for doc in docs]
        except Exception as e:
            print(f"[HospitalFirebaseService] Firestore read error: {e}", flush=True)

        # 2. Fallback JSON (Secours)
        try:
            # Remonte de 2 niveaux depuis 'app/services' pour trouver 'app/static/data'
            json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'data', 'hospitals.json')
            with open(json_path, 'r', encoding='utf-8') as f:
                hospitals = json.load(f)
                return hospitals
        except FileNotFoundError:
            print("[HospitalFirebaseService] Warning: hospitals.json not found", flush=True)
            return []
        except Exception as e:
            print(f"[HospitalFirebaseService] Fallback JSON error: {e}", flush=True)
            return []

    def find_nearest_hospital(self, patient_lat, patient_lon, patient_age=None, symptoms=None, **kwargs):
        """
        Trouve l'établissement le plus pertinent selon :
        - La distance
        - L'âge du patient (Filtre Pédiatrie)
        - Les symptômes (Recherche Spécialiste)
        - Le type d'établissement (Exclusion dentistes/cabinets)
        """
        hospitals = self.get_all_hospitals()
        if not hospitals:
            return None
        
        print(f"[HospitalService] Recherche - Age: {patient_age}, Symptômes: {symptoms}", flush=True)

        # --- CONFIGURATION DES FILTRES ---
        
        # Mots-clés pour inclusion automatique (Structures d'urgence)
        keywords_include = ['urgence', 'hopital', 'hôpital', 'clinique', 'chu', 'polyclinique', 'sanatorium', 'centre hospitalier']
        
        # Mots-clés pour exclusion stricte
        keywords_exclude = [
            'dentaire', 'dentiste', 'dental', 
            'vétérinaire', 'veterinary', 'animale',
            'kiné', 'massage', 'optique', 'ophtalmo',
            'cabinet', 'esthetique', 'laboratoire', 'analyse', 'radiologie'
        ]

        # --- 1. GESTION DE L'AGE (Filtrage Pédiatrie) ---
        try:
            if patient_age is not None:
                # Nettoyage de la chaine (ex: "22 ans" -> 22)
                age_str = str(patient_age).lower().replace('ans', '').replace('years', '').strip()
                # On ne garde que les chiffres
                age_str = ''.join(filter(str.isdigit, age_str))
                
                if age_str:
                    age = int(age_str)
                    if age > 16: 
                        # Si Adulte : On interdit les pédiatres
                        keywords_exclude.extend(['pédiatre', 'pediatre', 'pediatrie', 'enfant'])
                    # Si Enfant (<16) : On autorise tout (les pédiatres ET les hôpitaux généraux)
        except Exception as e:
            print(f"[HospitalService] Erreur filtre âge: {e}", flush=True)

        # --- 2. GESTION DES SYMPTÔMES (Mapping Spécialistes) ---
        priority_keywords = []
        if symptoms:
            s = str(symptoms).lower()
            
            # PNEUMOLOGIE (Respiration)
            if any(x in s for x in ['respir', 'souffle', 'etouff', 'toux', 'gorge', 'air']):
                priority_keywords.extend(['pneumo', 'poumon', 'respiratoire', 'thorax'])
            
            # CARDIOLOGIE (Cœur, Poitrine)
            if any(x in s for x in ['coeur', 'cœur', 'poitrine', 'cardiaque', 'infarctus', 'bras gauche', 'palpitation']):
                priority_keywords.extend(['cardio', 'cœur', 'coeur', 'vasculaire'])
            
            # TRAUMATOLOGIE (Accident, Os)
            if any(x in s for x in ['accident', 'chute', 'tomber', 'os', 'cassé', 'fracture', 'sang', 'coupure', 'jambe', 'bras']):
                priority_keywords.extend(['trauma', 'ortho', 'chirurgie'])
            
            # NEUROLOGIE (Tête, Malaise)
            if any(x in s for x in ['tête', 'tete', 'vertige', 'malaise', 'vanou', 'conscience', 'paralysi']):
                priority_keywords.extend(['neuro', 'cerveau'])
                
            # MATERNITÉ
            if any(x in s for x in ['enceinte', 'bebe', 'bébé', 'accouch', 'ventre', 'grossesse']):
                priority_keywords.extend(['maternité', 'accouchement', 'gyneco', 'obstétri'])

        # --- 3. FILTRAGE DES CANDIDATS ---
        eligible_hospitals = []
        
        for h in hospitals:
            name_lower = h.get('name', '').lower()
            specialties = str(h.get('specialties', [])).lower()
            
            # A. Exclusion stricte (Stop immédiat si mot interdit trouvé)
            if any(bad_word in name_lower for bad_word in keywords_exclude):
                continue

            is_candidate = False

            # B. Inclusion par défaut (C'est un Hôpital ou une Clinique ?)
            if any(good_word in name_lower for good_word in keywords_include):
                is_candidate = True
            
            # C. Inclusion par spécialité explicite "Urgences"
            if 'urgence' in specialties:
                is_candidate = True
            
            # D. Inclusion FORCEE par symptôme (BOOST SPÉCIALISTE)
            # Si le nom ou la spécialité matche le symptôme, on prend même si ce n'est pas un "Hôpital"
            # (Ex: "Centre de Cardiologie" sera accepté pour une douleur poitrine)
            if any(k in name_lower or k in specialties for k in priority_keywords):
                is_candidate = True

            if is_candidate:
                eligible_hospitals.append(h)

        # Si le filtrage est trop strict et vide la liste, on reprend tout sauf les exclus
        candidates = eligible_hospitals if eligible_hospitals else [h for h in hospitals if not any(b in h.get('name','').lower() for b in keywords_exclude)]
        
        if not candidates:
            return None

        # --- 4. CALCUL DE DISTANCE ---
        hospitals_with_distance = []
        for hospital in candidates:
            distance = self.haversine_distance(
                patient_lat, patient_lon,
                hospital['lat'], hospital['lng']
            )
            hospitals_with_distance.append({
                'hospital': hospital,
                'distance': distance
            })
        
        # Tri du plus proche au plus loin
        hospitals_with_distance.sort(key=lambda x: x['distance'])
        
        nearest_obj = hospitals_with_distance[0]['hospital']
        dist_vol_oiseau = round(hospitals_with_distance[0]['distance'], 2)
        
        # --- 5. CALCUL ITINÉRAIRE RÉEL (ORS) ---
        route_data = {}
        try:
            # Import différé pour éviter les cycles
            from app.services.ors_service import ORSService
            ors = ORSService()
            route_data = ors.get_route(
                start_coords=[patient_lon, patient_lat],
                end_coords=[nearest_obj['lng'], nearest_obj['lat']]
            )
        except Exception as e:
            print(f"[HospitalService] Erreur ORS: {e}", flush=True)
            # Fallback simple
            route_data = {
                'distance_km': dist_vol_oiseau,
                'duration_min': int(dist_vol_oiseau * 2), # Estimation grossière (30km/h)
                'geometry': ''
            }
        
        # Construction de la réponse finale
        return {
            'id': nearest_obj.get('id', nearest_obj.get('name')).replace(' ', '_'),
            'name': nearest_obj['name'],
            'service': 'Urgences', # Standardisé pour l'affichage
            'distance_km': route_data.get('distance_km', dist_vol_oiseau),
            'eta_minutes': route_data.get('duration_min', 15),
            'coordinates': {'lat': nearest_obj['lat'], 'lng': nearest_obj['lng']},
            'locality': nearest_obj.get('locality', ''),
            'route_geometry': route_data.get('geometry', '')
        }
    
    def add_hospital(self, hospital_data):
        """Ajoute un nouvel hôpital"""
        return self.collection.add(hospital_data)
    
    def update_hospital(self, hospital_id, hospital_data):
        """Met à jour un hôpital existant"""
        self.collection.document(hospital_id).update(hospital_data)

    def delete_hospital(self, hospital_id):
        """Supprime un hôpital"""
        self.collection.document(hospital_id).delete()