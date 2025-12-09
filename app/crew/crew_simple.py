import yaml
import os
from langchain_groq import ChatGroq
from app.config_settings import Config
from app.services.hospital_service import HospitalService
from app.services.ors_service import ORSService
import json
from datetime import datetime

class MediAlertCrew:
    def __init__(self):
        self.llm = ChatGroq(
            model=Config.GROQ_MODEL,
            api_key=Config.GROQ_API_KEY,
            temperature=0.3
        )
        self.hospital_service = HospitalService()
        self.ors_service = ORSService()
        self._load_configurations()
    
    def _load_configurations(self):
        """Load agents and tasks from YAML files"""
        config_dir = os.path.join(os.path.dirname(__file__), 'config')
        
        # Load agents
        with open(os.path.join(config_dir, 'agents.yaml'), 'r', encoding='utf-8') as f:
            self.agents_config = yaml.safe_load(f)
        
        # Load tasks
        with open(os.path.join(config_dir, 'tasks.yaml'), 'r', encoding='utf-8') as f:
            self.tasks_config = yaml.safe_load(f)
    
    def execute_emergency_response(self, inputs):
        """Execute the complete emergency response workflow"""
        results = {}
        
        print("\n" + "="*70, flush=True)
        print("  MEDIALERT SMA - SYSTÈME MULTI-AGENTS D'URGENCE MÉDICALE", flush=True)
        print("="*70, flush=True)
        print(f"\nPatient: {inputs.get('nom_prenom', 'N/A')}", flush=True)
        print(f"Âge: {inputs.get('age', 'N/A')} ans", flush=True)
        print(f"Sexe: {inputs.get('sexe', 'N/A')}", flush=True)
        print(f"Symptômes: {inputs.get('symptomes', 'N/A')}", flush=True)
        print(f"Localisation: {inputs.get('localisation', 'N/A')}", flush=True)
        print("\n" + "-"*70 + "\n", flush=True)
        
        try:
            # Task 1: Create Alert
            print("\n[AGENT PATIENT] Création de l'alerte...", flush=True)
            alert_result = self._execute_task('creer_l_alerte', inputs)
            results['alert'] = alert_result
            print(f"[AGENT PATIENT] ✓ Alerte créée: {alert_result.get('alerte_patient', {}).get('id_alerte', 'N/A')}", flush=True)
            print(f"[AGENT PATIENT] JSON Output:\n{json.dumps(alert_result, indent=2, ensure_ascii=False)}\n", flush=True)
            
            # Task 2: Medical Analysis
            print("\n[AGENT MÉDECIN URGENCE] Analyse médicale en cours...", flush=True)
            medical_result = self._execute_task('analyse_medicale_d_urgence', inputs, alert_result)
            results['medical'] = medical_result
            triage = medical_result.get('triage_medical', {})
            print(f"[AGENT MÉDECIN URGENCE] ✓ Niveau d'urgence: {triage.get('niveau_urgence', 'N/A')}", flush=True)
            print(f"[AGENT MÉDECIN URGENCE] ✓ Score CCMU: {triage.get('score_ccmu', 'N/A')}", flush=True)
            print(f"[AGENT MÉDECIN URGENCE] ✓ Type de vecteur: {triage.get('type_vecteur', 'N/A')}", flush=True)
            print(f"[AGENT MÉDECIN URGENCE] JSON Output:\n{json.dumps(medical_result, indent=2, ensure_ascii=False)}\n", flush=True)
            
            # Task 3: Coordinator Decision (with hospital search)
            print("\n[AGENT COORDONNATEUR] Sélection hôpital et ambulance...", flush=True)
            coordinator_result = self._execute_coordinator_task(inputs, alert_result, medical_result)
            results['coordinator'] = coordinator_result
            hospital = coordinator_result.get('selected_hospital', {})
            print(f"[AGENT COORDONNATEUR] ✓ Hôpital sélectionné: {hospital.get('name', 'N/A')}", flush=True)
            print(f"[AGENT COORDONNATEUR] ✓ Distance: {hospital.get('distance_km', 'N/A')} km", flush=True)
            print(f"[AGENT COORDONNATEUR] ✓ ETA: {hospital.get('eta_minutes', 'N/A')} minutes", flush=True)
            print(f"[AGENT COORDONNATEUR] ✓ Localisation: {hospital.get('locality', 'N/A')}", flush=True)
            print(f"[AGENT COORDONNATEUR] JSON Output:\n{json.dumps(coordinator_result, indent=2, ensure_ascii=False, default=str)}\n", flush=True)
            
            # Task 4: Ambulance Route Calculation
            print("\n[AGENT AMBULANCE] Calcul de l'itinéraire...", flush=True)
            ambulance_result = self._execute_ambulance_task(inputs, coordinator_result)
            results['ambulance'] = ambulance_result
            logistique = ambulance_result.get('logistique', {})
            print(f"[AGENT AMBULANCE] ✓ ETA patient: {logistique.get('eta_patient_minutes', 'N/A')} minutes", flush=True)
            print(f"[AGENT AMBULANCE] ✓ ETA hôpital: {logistique.get('eta_hopital_minutes', 'N/A')} minutes", flush=True)
            print(f"[AGENT AMBULANCE] ✓ Distance totale: {logistique.get('distance_totale_km', 'N/A')} km", flush=True)
            print(f"[AGENT AMBULANCE] JSON Output:\n{json.dumps(ambulance_result, indent=2, ensure_ascii=False, default=str)}\n", flush=True)
            
            # Task 5: Hospital Preparation
            print("\n[AGENT HÔPITAL] Préparation de l'accueil...", flush=True)
            hospital_result = self._execute_task('recevoir_les_patients', inputs, medical_result, ambulance_result)
            results['hospital'] = hospital_result
            print(f"[AGENT HÔPITAL] ✓ Lit assigné: {hospital_result.get('preparation_hopital', {}).get('numero_lit', 'N/A')}", flush=True)
            print(f"[AGENT HÔPITAL] JSON Output:\n{json.dumps(hospital_result, indent=2, ensure_ascii=False)}\n", flush=True)
            
            # Task 6: Specialist Protocols
            print("\n[AGENT MÉDECIN SPÉCIALISTE] Protocoles de traitement...", flush=True)
            specialist_result = self._execute_task('traitement_du_specialiste', inputs, medical_result)
            results['specialist'] = specialist_result
            print(f"[AGENT MÉDECIN SPÉCIALISTE] ✓ Protocole défini", flush=True)
            print(f"[AGENT MÉDECIN SPÉCIALISTE] JSON Output:\n{json.dumps(specialist_result, indent=2, ensure_ascii=False)}\n", flush=True)
            
            # Task 7: Final UI Consolidation
            print("\n[AGENT ADMINISTRATIF] Consolidation du dossier...", flush=True)
            ui_result = self._execute_final_task(inputs, results)
            results['ui'] = ui_result
            print(f"[AGENT ADMINISTRATIF] ✓ Dossier consolidé", flush=True)
            print(f"[AGENT ADMINISTRATIF] JSON Output:\n{json.dumps(ui_result, indent=2, ensure_ascii=False, default=str)}\n", flush=True)
            
            # Final Summary
            print("\n" + "="*70, flush=True)
            print("  ✅ MISSION TERMINÉE - RÉSUMÉ DE L'INTERVENTION", flush=True)
            print("="*70, flush=True)
            hospital = results.get('coordinator', {}).get('selected_hospital', {})
            logistique = results.get('ambulance', {}).get('logistique', {})
            triage = results.get('medical', {}).get('triage_medical', {})
            print(f"\nHôpital: {hospital.get('name', 'N/A')}", flush=True)
            print(f"Distance: {hospital.get('distance_km', 'N/A')} km", flush=True)
            print(f"ETA Patient: {logistique.get('eta_patient_minutes', 'N/A')} min", flush=True)
            print(f"ETA Hôpital: {logistique.get('eta_hopital_minutes', 'N/A')} min", flush=True)
            print(f"Niveau d'urgence: {triage.get('niveau_urgence', 'N/A')}", flush=True)
            print(f"Type ambulance: {triage.get('type_vecteur', 'N/A')}", flush=True)
            print("\n" + "="*70 + "\n", flush=True)
            
            return results
            
        except Exception as e:
            print(f"\n[ERROR] {str(e)}\n", flush=True)
            return {'error': str(e), 'partial_results': results}
    
    def _execute_task(self, task_name, inputs, *context_results):
        """Execute a single task using Groq LLM"""
        task_config = self.tasks_config[task_name]
        agent_name = task_config['agent']
        
        # Map task agent names to actual agent config names
        agent_map = {
            'agentpatient': 'emetteur_d_alerte',
            'agentmedecinurgence': 'medical_regulation_ai_triage',
            'agentcordonnateur': 'operational_regulation_chief',
            'agentambulence': 'mobile_intervention_pilot',
            'agenthopital': 'hospital_resource_manager',
            'agentmedecinspecialiste': 'clinical_protocols_engine',
            'agentadministratif': 'patient_interface_reporting'
        }
        
        actual_agent_name = agent_map.get(agent_name, agent_name)
        agent_config = self.agents_config[actual_agent_name]
        
        # Build context from previous results
        context_text = ""
        if context_results:
            context_text = "\n\nContext from previous tasks:\n"
            for i, result in enumerate(context_results):
                context_text += f"Result {i+1}: {json.dumps(result, indent=2)}\n"
        
        # Create prompt
        prompt = f"""
Role: {agent_config['role']}
Goal: {agent_config['goal']}
Backstory: {agent_config['backstory']}

Task Description: {task_config['description'].format(**inputs)}
Expected Output: {task_config['expected_output']}

{context_text}

Please execute this task and provide the output in the exact JSON format specified.
"""
        
        # Execute with Groq
        response = self.llm.invoke(prompt)
        
        try:
            # Try to parse JSON response
            result = json.loads(response.content)
            return result
        except json.JSONDecodeError:
            # Fallback: extract JSON from response
            content = response.content
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end != 0:
                try:
                    result = json.loads(content[start:end])
                    return result
                except:
                    pass
            
            # Final fallback: return structured response
            return {
                'task': task_name,
                'status': 'completed',
                'raw_response': content,
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _execute_coordinator_task(self, inputs, alert_result, medical_result):
        """Execute coordinator task with hospital search integration"""
        # Default coordinates (Casablanca)
        lat, lon = 33.5731, -7.5898
        
        # Find strictly nearest hospital using Haversine + ORS
        nearest_hospital = self.hospital_service.find_nearest_hospital(lat, lon)
        
        # Execute coordinator task
        task_config = self.tasks_config['triage_patients_et_selection_ambulance']
        agent_config = self.agents_config['operational_regulation_chief']
        
        prompt = f"""
Role: {agent_config['role']}
Goal: {agent_config['goal']}
Backstory: {agent_config['backstory']}

Task: {task_config['description'].format(**inputs)}

Nearest Hospital (Validated):
{json.dumps(nearest_hospital, indent=2)}

Medical Analysis:
{json.dumps(medical_result, indent=2)}

Please confirm hospital assignment in required JSON format:
{task_config['expected_output']}
"""
        
        response = self.llm.invoke(prompt)
        
        try:
            result = json.loads(response.content)
            result['selected_hospital'] = nearest_hospital
            return result
        except:
            return {
                'decision_operationnelle': {
                    'statut': 'ASSIGNED',
                    'ambulance_id': 'AMB-001',
                    'type_ambulance': 'SMUR',
                    'hopital_cible_id': nearest_hospital['id'],
                    'service_cible': nearest_hospital['service'],
                    'raison_choix': f"Hôpital le plus proche: {nearest_hospital['distance_km']} km"
                },
                'selected_hospital': nearest_hospital
            }
    
    def _execute_ambulance_task(self, inputs, coordinator_result):
        """Execute ambulance task with route calculation"""
        # Get coordinates from selected hospital
        hospital = coordinator_result.get('selected_hospital', {})
        patient_coords = [33.5731, -7.5898]  # Default
        hospital_coords = [hospital.get('coordinates', {}).get('lat', 33.5892), 
                          hospital.get('coordinates', {}).get('lng', -7.6031)]
        
        # Use route geometry if already calculated
        if 'route_geometry' in hospital:
            route_data = {
                'distance_km': hospital['distance_km'],
                'duration_min': hospital['eta_minutes'],
                'geometry': hospital['route_geometry']
            }
        else:
            # Calculate route using ORS
            route_data = self.ors_service.get_route(
                start_coords=[patient_coords[1], patient_coords[0]],
                end_coords=[hospital_coords[1], hospital_coords[0]]
            )
        
        # Execute ambulance task
        task_config = self.tasks_config['valider_la_demande_du_coordonnateur']
        agent_config = self.agents_config['mobile_intervention_pilot']
        
        prompt = f"""
Role: {agent_config['role']}
Goal: {agent_config['goal']}
Backstory: {agent_config['backstory']}

Task: {task_config['description']}

Route Calculation Results:
{json.dumps(route_data, indent=2)}

Coordinator Decision:
{json.dumps(coordinator_result, indent=2)}

Please provide the logistics information in the required JSON format:
{task_config['expected_output']}
"""
        
        response = self.llm.invoke(prompt)
        
        try:
            result = json.loads(response.content)
            # Add route data for frontend
            result['route_data'] = route_data
            return result
        except:
            return {
                'logistique': {
                    'eta_patient_minutes': route_data.get('duration_min', 8),
                    'eta_hopital_minutes': route_data.get('duration_min', 8) + 15,
                    'distance_totale_km': route_data.get('distance_km', 2.5),
                    'polyline_route': route_data.get('geometry', ''),
                    'heure_arrivee_estimee': datetime.utcnow().isoformat()
                },
                'route_data': route_data
            }
    
    def _execute_final_task(self, inputs, all_results):
        """Execute final UI consolidation task"""
        task_config = self.tasks_config['consolider_dossier_pour_ui']
        agent_config = self.agents_config['patient_interface_reporting']
        
        prompt = f"""
Role: {agent_config['role']}
Goal: {agent_config['goal']}
Backstory: {agent_config['backstory']}

Task: {task_config['description']}

All Previous Results:
{json.dumps(all_results, indent=2, default=str)}

Please consolidate all information into the final UI format:
{task_config['expected_output']}
"""
        
        response = self.llm.invoke(prompt)
        
        try:
            result = json.loads(response.content)
            return result
        except:
            # Fallback UI result
            eta_minutes = 8
            if 'ambulance' in all_results and 'logistique' in all_results['ambulance']:
                eta_minutes = all_results['ambulance']['logistique'].get('eta_patient_minutes', 8)
            
            return {
                'ui_view': {
                    'message_patient': f'Une équipe médicale arrive dans {eta_minutes} minutes',
                    'timeline': {
                        'alerte_recue': datetime.utcnow().isoformat(),
                        'triage_effectue': datetime.utcnow().isoformat(),
                        'ambulance_en_route': datetime.utcnow().isoformat()
                    },
                    'details_techniques': {
                        'ambulance': all_results.get('ambulance', {}),
                        'hopital': all_results.get('coordinator', {}).get('selected_hospital', {}),
                        'medical': all_results.get('medical', {})
                    }
                }
            }
