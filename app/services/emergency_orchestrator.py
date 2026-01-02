import asyncio
import json
from datetime import datetime
from firebase_admin import firestore
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from app.config_settings import Config
from app.services.firebase_service import FirebaseService
from app.services.hospital_firebase_service import HospitalFirebaseService
from app.services.ambulance_firebase_service import AmbulanceFirebaseService
from app.services.ors_service import ORSService

class EmergencyOrchestrator:
    """
    Orchestrateur Hybride :
    - Logique Rapide (Python) : Géolocalisation, Choix Hôpital, Trajets, Triage initial.
    - Logique IA (Llama-3) : Uniquement pour l'Agent Spécialiste (Protocoles de soins).
    """
    
    def __init__(self):
        # Services Standards
        self.firebase = FirebaseService()
        self.hospital_service = HospitalFirebaseService()
        self.ambulance_service = AmbulanceFirebaseService()
        self.ors_service = ORSService()
        self.alerts_collection = self.firebase.get_collection('alerts')
        
        # --- INITIALISATION IA (Pour l'Agent Spécialiste uniquement) ---
        try:
            self.llm = ChatGroq(
                api_key=Config.GROQ_API_KEY,
                model_name="llama-3.3-70b-versatile",
                temperature=0.3
            )
            print("✅ [IA] Llama-3.3 connectée pour l'Agent Spécialiste.")
        except Exception as e:
            print(f"⚠️ [IA] Erreur connexion Groq: {e}")
            self.llm = None

    def log_agent(self, agent_role, action, content):
        """Logs colorés dans le terminal"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        colors = {
            "Emetteur d'Alerte": "\033[96m",      # Cyan
            "Medical Regulation AI": "\033[95m",  # Violet
            "Operational Regulation Chief": "\033[93m", # Jaune
            "Mobile Intervention Pilot": "\033[91m",    # Rouge
            "Clinical Protocols Engine": "\033[97m", # BLANC (L'Agent IA)
            "Hospital Resource Manager": "\033[92m",    # Vert
            "END": "\033[0m"
        }
        c = colors.get(agent_role, "")
        end = colors["END"]
        print(f"{c}[{timestamp}] 🤖 AGENT: {agent_role}{end}")
        print(f"{c}   └─ ACTION: {action}{end}")
        print(f"{c}   └─ OUTPUT: {content}{end}\n")

    def update_status(self, alert_id, status, logs_list, data=None):
        """Mise à jour Firestore"""
        update_data = {
            'status': status,
            'updated_at': datetime.utcnow().isoformat()
        }
        if logs_list and len(logs_list) > 0:
            update_data['logs'] = firestore.ArrayUnion(logs_list)
        if data:
            update_data.update(data)
        try:
            self.alerts_collection.document(alert_id).update(update_data)
        except Exception as e:
            print(f"[SYSTEM ERROR] Firestore Update: {e}")

    # --- TÂCHE SPÉCIFIQUE DE L'AGENT SPÉCIALISTE (VIA LLAMA) ---
    async def run_specialist_agent(self, symptomes, age, ccmu):
        """
        Cet agent utilise l'IA pour générer les 'SOP' (Standard Operating Procedures)
        basés sur le diagnostic suspecté.
        """
        if not self.llm:
            return None

        print("\n🧠 [IA] Agent Spécialiste : Analyse des protocoles en cours...")

        prompt = ChatPromptTemplate.from_template(
            """Tu es l'agent 'Clinical Protocols Engine' (Médecin Spécialiste).
            Ta mission : Générer une checklist et des protocoles de soins standardisés (SOP) pour l'équipe sur le terrain.
            
            DONNÉES PATIENT :
            - Âge : {age} ans
            - Symptômes : {symptomes}
            - Score CCMU : {ccmu}
            
            Génère un JSON STRICT (sans texte autour) avec cette structure exacte :
            {{
                "diagnostic_suspecte": "Hypothèse médicale principale (ex: Syndrome Coronarien Aigu)",
                "protocole_transport": "Gestes techniques immédiats à faire dans l'ambulance (phrase courte et précise)",
                "checklist_accueil": ["Action 1 pour l'hôpital", "Action 2", "Action 3"],
                "medicaments_a_preparer": ["Nom Médicament 1", "Nom Médicament 2"]
            }}
            """
        )
        
        try:
            chain = prompt | self.llm
            response = await chain.ainvoke({"age": age, "symptomes": symptomes, "ccmu": ccmu})
            
            # Nettoyage du JSON (retrait des balises Markdown éventuelles)
            content = response.content.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].strip()
                
            return json.loads(content)
        except Exception as e:
            print(f"❌ Erreur Agent Spécialiste: {e}")
            return None

    async def simulate_driving(self, alert_id, route_coords, ambulance):
        """Simulation physique du déplacement"""
        print(f"🚑 [SIMULATION] Route de {len(route_coords)} points.")
        steps = route_coords[::3] 
        for point in steps:
            ambulance['current_lat'] = point[0] 
            ambulance['current_lng'] = point[1]
            self.update_status(alert_id, 'MOVING', [], {'ambulance': ambulance})
            await asyncio.sleep(0.6)

    # --- WORKFLOW PRINCIPAL ---
    async def run_workflow(self, alert_id, patient_lat, patient_lng, emergency_level, symptomes="Non spécifié", age="Inconnu"):
        try:
            print("\n" + "="*60)
            print(f"🚀 DÉMARRAGE WORKFLOW (ID: {alert_id})")
            print("="*60 + "\n")

            # --- PHASE 1 : AGENT PATIENT (Algo) ---
            self.log_agent("Emetteur d'Alerte", "Normalisation", f"Signal reçu. Symptômes: {symptomes}")
            await asyncio.sleep(1)

            # --- PHASE 2 : AGENT RÉGULATEUR (Algo Rapide pour Triage) ---
            ccmu_score = 3 if emergency_level >= 2 else 1
            vecteur = "SMUR (UMH)" if ccmu_score >= 3 else "Ambulance Standard"
            self.log_agent("Medical Regulation AI", "Triage Initial", f"Score CCMU {ccmu_score}. Vecteur: {vecteur}.")
            await asyncio.sleep(1)

            # --- PHASE 3 : AGENT COORDINATEUR (Algo Géographique) ---
            hospital = self.hospital_service.find_nearest_hospital(patient_lat, patient_lng)
            self.log_agent("Operational Regulation Chief", "Orchestration", f"Hôpital {hospital['name']} verrouillé.")
            await asyncio.sleep(1)

            # --- PHASE 4 : LOGISTIQUE & ROUTING (ORS) ---
            ambulances = self.ambulance_service.get_available_by_level(emergency_level)
            ambulance = ambulances[0] if ambulances else {'id': 'SMUR-01', 'current_lat': 33.24, 'current_lng': -8.50}
            
            # Calculs Itinéraires
            amb_coords = [ambulance.get('current_lng'), ambulance.get('current_lat')]
            pat_coords = [patient_lng, patient_lat]
            hosp_coords = [hospital['coordinates']['lng'], hospital['coordinates']['lat']]
            
            route_red = self.ors_service.get_route(amb_coords, pat_coords)
            route_blue = self.ors_service.get_route(pat_coords, hosp_coords)
            
            self.update_status(alert_id, 'DISPATCHED', 
                ["Ambulance en route vers le patient."],
                {
                    'ambulance': ambulance, 'selected_hospital': hospital,
                    'route_red': json.dumps(route_red.get('coordinates', [])),
                    'route_active': 'RED', 'eta_minutes': route_red.get('duration_min', 5)
                })

            # --- PHASE 5 : MOUVEMENT VERS PATIENT ---
            path_to_patient = route_red.get('coordinates', [])
            if path_to_patient: await self.simulate_driving(alert_id, path_to_patient, ambulance)

            # --- ARRIVÉE & INTERVENTION DE L'AGENT SPÉCIALISTE (LLAMA) ---
            self.update_status(alert_id, 'PATIENT_PICKUP', ["Arrivée sur site. Activation Agent Spécialiste..."])
            
            # APPEL À L'IA ICI SEULEMENT
            protocol_data = await self.run_specialist_agent(symptomes, age, ccmu_score)
            
            if protocol_data:
                # Formatage pour les logs
                diag = protocol_data.get('diagnostic_suspecte', 'Non déterminé')
                actions = protocol_data.get('protocole_transport', 'Standard')
                meds = ", ".join(protocol_data.get('medicaments_a_preparer', []))
                
                self.log_agent("Clinical Protocols Engine", "Génération SOP", 
                            f"\n - Diagnostic: {diag}\n - Protocole: {actions}\n - Meds: {meds}")
                
                # --- MODIFICATION ICI : On envoie tout le détail dans les logs de la console ---
                logs_ui = [
                    f"Spécialiste: Diagnostic -> {diag}",
                    f"Spécialiste: Action -> {actions}",  # <-- L'action sera affichée
                    f"Spécialiste: Meds -> {meds}"        # <-- Les médicaments seront affichés
                ]
                
                self.update_status(alert_id, 'PROTOCOL_GENERATED', 
                    logs_ui,
                    {'medical_protocol': protocol_data}
                )
            
            await asyncio.sleep(4) # Temps pour lire le protocole

            # --- PHASE 6 : TRANSPORT VERS HÔPITAL ---
            self.update_status(alert_id, 'EN_ROUTE_TO_HOSPITAL', ["Départ vers l'hôpital."],
                {'route_blue': json.dumps(route_blue.get('coordinates', [])), 'route_active': 'BLUE'})
            
            path_to_hospital = route_blue.get('coordinates', [])
            if path_to_hospital: await self.simulate_driving(alert_id, path_to_hospital, ambulance)

            # --- EXTRACTION ET SAUVEGARDE DES DONNÉES FINALES ---
            # Calculer les données finales pour l'UI
            total_distance = route_red.get('distance_km', 0) + route_blue.get('distance_km', 0)
            total_eta = route_red.get('duration_min', 0) + route_blue.get('duration_min', 0)
            
            # Créer l'équipe médicale
            medical_team = [
                {"name": "Dr. Martin Dubois", "specialty": "Urgentiste"},
                {"name": "Inf. Sarah Benali", "specialty": "Infirmière SMUR"}
            ]
            
            # Données finales à sauvegarder
            final_data = {
                'hospital_name': hospital['name'],
                'distance_km': total_distance,
                'eta_minutes': total_eta,
                'arrival_time': datetime.utcnow().isoformat(),
                'medical_team': medical_team
            }
            
            # --- FIN ---
            self.update_status(alert_id, 'RESOLVED', ["Patient admis. Mission terminée."], final_data)
            print("✅ MISSION TERMINÉE")

        except Exception as e:
            print(f"❌ ERROR: {e}")
            self.update_status(alert_id, 'ERROR', [f"Erreur: {str(e)}"])