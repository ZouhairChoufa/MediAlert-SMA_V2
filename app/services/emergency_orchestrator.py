import asyncio
import time
import json
from datetime import datetime
from firebase_admin import firestore
from app.services.firebase_service import FirebaseService
from app.services.hospital_firebase_service import HospitalFirebaseService
from app.services.ambulance_firebase_service import AmbulanceFirebaseService
from app.services.ors_service import ORSService

class EmergencyOrchestrator:
    """Orchestrates emergency workflow with realistic delays"""
    
    def __init__(self):
        self.firebase = FirebaseService()
        self.hospital_service = HospitalFirebaseService()
        self.ambulance_service = AmbulanceFirebaseService()
        self.ors_service = ORSService()
        self.alerts_collection = self.firebase.get_collection('alerts')
    
    def update_status(self, alert_id, status, message, data=None):
        """Update alert status in Firestore"""
        update_data = {
            'status': status,
            'logs': firestore.ArrayUnion([f"[{datetime.utcnow().strftime('%H:%M:%S')}] {message}"]),
            'updated_at': datetime.utcnow().isoformat()
        }
        if data:
            update_data.update(data)
        self.alerts_collection.document(alert_id).update(update_data)
    
    async def run_workflow(self, alert_id, patient_lat, patient_lng, emergency_level):
        """Execute emergency workflow with delays"""
        try:
            # STEP 1: Coordinator Analysis
            self.update_status(alert_id, 'SEARCHING_HOSPITALS', 
                              'Coordinator Agent: Analyzing incoming alert...')
            await asyncio.sleep(2)
            
            # Find best hospital
            hospital = self.hospital_service.find_nearest_hospital(patient_lat, patient_lng)
            if not hospital:
                self.update_status(alert_id, 'ERROR', 'No hospitals available')
                return
            
            self.update_status(alert_id, 'HOSPITAL_SELECTED',
                              f"Coordinator: Hospital {hospital['name']} selected ({hospital['distance_km']}km away)",
                              {'selected_hospital': hospital})
            await asyncio.sleep(1)
            
            # STEP 2: Ambulance Dispatch
            self.update_status(alert_id, 'DISPATCHING_AMBULANCE',
                              'Dispatching nearest ambulance...')
            await asyncio.sleep(1)
            
            # Find ambulance
            ambulances = self.ambulance_service.get_available_by_level(emergency_level)
            if not ambulances:
                self.update_status(alert_id, 'ERROR', 'No ambulances available')
                return
            
            ambulance = ambulances[0]
            ambulance_lat = ambulance.get('current_lat', 33.5731)
            ambulance_lng = ambulance.get('current_lng', -7.5898)
            
            # STEP 3: Route to Patient (Phase 1)
            try:
                route_to_patient = self.ors_service.get_route(
                    start_coords=[ambulance_lng, ambulance_lat],
                    end_coords=[patient_lng, patient_lat]
                )
                eta_to_patient = route_to_patient.get('duration_min', 5)
                route_geometry_patient = route_to_patient.get('geometry', '')
            except Exception as e:
                # Fallback to mock data if ORS fails
                eta_to_patient = 5
                route_geometry_patient = json.dumps([[ambulance_lat, ambulance_lng], [patient_lat, patient_lng]])
            
            self.update_status(alert_id, 'EN_ROUTE_TO_PATIENT',
                              f"Ambulance {ambulance['id']} dispatched. ETA to patient: {eta_to_patient} mins",
                              {
                                  'ambulance': ambulance,
                                  'route_phase': 'TO_PATIENT',
                                  'route_geometry': route_geometry_patient,
                                  'eta_minutes': eta_to_patient
                              })
            
            # Simulate travel to patient
            await asyncio.sleep(5)
            
            # STEP 4: Arrival at Patient
            self.update_status(alert_id, 'PATIENT_PICKUP',
                              'Ambulance has arrived at patient location. Stabilizing patient...')
            await asyncio.sleep(3)
            
            # STEP 5: Route to Hospital (Phase 2)
            try:
                route_to_hospital = self.ors_service.get_route(
                    start_coords=[patient_lng, patient_lat],
                    end_coords=[hospital['coordinates']['lng'], hospital['coordinates']['lat']]
                )
                eta_to_hospital = route_to_hospital.get('duration_min', 8)
                route_geometry_hospital = route_to_hospital.get('geometry', '')
            except Exception as e:
                # Fallback to mock data if ORS fails
                eta_to_hospital = 8
                route_geometry_hospital = json.dumps([[patient_lat, patient_lng], [hospital['coordinates']['lat'], hospital['coordinates']['lng']]])
            
            self.update_status(alert_id, 'EN_ROUTE_TO_HOSPITAL',
                              f"En route to Hospital {hospital['name']}. ETA: {eta_to_hospital} mins",
                              {
                                  'route_phase': 'TO_HOSPITAL',
                                  'route_geometry': route_geometry_hospital,
                                  'eta_minutes': eta_to_hospital
                              })
            
            # Simulate travel to hospital
            await asyncio.sleep(5)
            
            # STEP 6: Arrival at Hospital
            self.update_status(alert_id, 'RESOLVED',
                              f"Patient admitted to {hospital['name']}. Mission Complete.",
                              {
                                  'completed_at': datetime.utcnow().isoformat(),
                                  'total_time_minutes': eta_to_patient + 3 + eta_to_hospital
                              })
        except Exception as e:
            self.update_status(alert_id, 'ERROR', f'Workflow error: {str(e)}')
