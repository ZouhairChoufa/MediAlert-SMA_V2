from flask import Blueprint, request, jsonify, session
from groq import Groq
import json
import re
from app.decorators import login_required
from app.models.patient import PatientStore
from app.services.infermedica_service import InfermedicaService
from app.config_settings import Config

chatbot_bp = Blueprint('chatbot', __name__)
patient_store = PatientStore()
infermedica = InfermedicaService()

# Initialize Groq client
groq_client = Groq(api_key=Config.GROQ_API_KEY)

@chatbot_bp.route('/api/chatbot/message', methods=['POST'])
@login_required
def chatbot_message():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get user profile for age/sex
        username = session.get('user')
        patient = patient_store.get_profile(username)
        
        if not patient:
            return jsonify({
                'response': "Je dois d'abord connaître votre profil médical. Veuillez créer votre profil patient pour continuer.",
                'needs_profile': True
            })
        
        # Phase 1: Groq extracts symptoms
        extraction_response = extract_symptoms_with_groq(user_message)
        
        # Check if Groq needs more information
        if extraction_response.get('needs_clarification'):
            return jsonify({
                'response': extraction_response['clarification_question'],
                'type': 'clarification'
            })
        
        # If symptoms identified, proceed to Infermedica
        symptoms = extraction_response.get('symptoms', [])
        if symptoms:
            # Get triage from Infermedica
            triage_result = infermedica.get_triage(
                symptoms, 
                patient.age, 
                patient.sexe
            )
            
            if triage_result:
                # Check for emergency
                triage_level = triage_result.get('triage_level', '').lower()
                if triage_level in ['emergency', 'ambulance']:
                    # Create emergency alert
                    create_emergency_alert(patient, user_message, triage_result)
                
                # Phase 2: Groq generates advice
                final_response = generate_advice_with_groq(
                    user_message, 
                    triage_result, 
                    patient
                )
                
                return jsonify({
                    'response': final_response,
                    'triage_level': triage_level,
                    'emergency_created': triage_level in ['emergency', 'ambulance']
                })
        
        # Fallback: General medical advice
        general_response = get_general_medical_advice(user_message)
        return jsonify({'response': general_response})
        
    except Exception as e:
        print(f"Chatbot error: {str(e)}")
        return jsonify({
            'response': "Je rencontre des difficultés techniques. Veuillez réessayer ou contacter un professionnel de santé si c'est urgent."
        }), 500

def extract_symptoms_with_groq(user_message):
    """Phase 1: Extract symptoms using Groq"""
    
    system_prompt = """Tu es un assistant médical expert en extraction de symptômes. 
    Ton rôle est d'analyser les messages des patients et d'extraire les symptômes médicaux standardisés.

    RÈGLES IMPORTANTES:
    1. Si le message contient des symptômes clairs, extrais-les au format JSON
    2. Si tu as besoin de plus d'informations, pose UNE question de clarification
    3. Sois précis et professionnel
    4. Ne donne JAMAIS de diagnostic ou de conseil médical à cette étape

    FORMAT DE RÉPONSE:
    - Si symptômes identifiés: {"symptoms": [{"name": "chest_pain", "severity": "severe"}], "needs_clarification": false}
    - Si clarification nécessaire: {"needs_clarification": true, "clarification_question": "Depuis quand ressentez-vous cette douleur?"}
    
    Symptômes courants à reconnaître: chest_pain, shortness_of_breath, headache, fever, nausea, dizziness, abdominal_pain, fatigue"""
    
    try:
        response = groq_client.chat.completions.create(
            model=Config.GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Message du patient: {user_message}"}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Try to parse JSON response
        try:
            return json.loads(result_text)
        except:
            # Fallback if JSON parsing fails
            return {
                "needs_clarification": True,
                "clarification_question": "Pouvez-vous me décrire plus précisément vos symptômes?"
            }
            
    except Exception as e:
        print(f"Groq extraction error: {str(e)}")
        return {
            "needs_clarification": True,
            "clarification_question": "Je n'ai pas bien compris. Pouvez-vous reformuler vos symptômes?"
        }

def generate_advice_with_groq(user_message, triage_result, patient):
    """Phase 2: Generate empathetic advice using Groq"""
    
    triage_level = triage_result.get('triage_level', '')
    conditions = triage_result.get('conditions', [])
    
    system_prompt = f"""Tu es MediBot, un assistant médical empathique et professionnel.
    
    CONTEXTE PATIENT:
    - Âge: {patient.age} ans
    - Sexe: {patient.sexe}
    - Message original: "{user_message}"
    
    RÉSULTATS MÉDICAUX:
    - Niveau de triage: {triage_level}
    - Conditions possibles: {conditions[:3] if conditions else 'Non spécifiées'}
    
    INSTRUCTIONS:
    1. Sois empathique et rassurant
    2. Explique clairement la situation
    3. Si niveau d'urgence élevé: mentionne que les secours ont été alertés
    4. Donne des conseils pratiques immédiats
    5. Recommande toujours de consulter un professionnel
    6. Utilise un langage simple et accessible
    7. Reste dans ton rôle d'assistant, ne pose pas de diagnostic définitif
    
    RÉPONSE EN FRANÇAIS, maximum 200 mots."""
    
    try:
        response = groq_client.chat.completions.create(
            model=Config.GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Génère une réponse appropriée basée sur ces informations médicales."}
            ],
            temperature=0.7,
            max_tokens=400
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"Groq advice generation error: {str(e)}")
        return "Je recommande de consulter rapidement un professionnel de santé pour évaluer vos symptômes."

def get_general_medical_advice(user_message):
    """Fallback for general medical questions"""
    
    system_prompt = """Tu es MediBot, un assistant médical bienveillant.
    Réponds aux questions générales de santé de manière informative mais prudente.
    
    RÈGLES:
    1. Ne pose jamais de diagnostic
    2. Recommande toujours de consulter un professionnel
    3. Donne des informations générales fiables
    4. Sois empathique et rassurant
    5. Maximum 150 mots
    6. Réponds en français"""
    
    try:
        response = groq_client.chat.completions.create(
            model=Config.GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.6,
            max_tokens=300
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"General advice error: {str(e)}")
        return "Je vous recommande de consulter un professionnel de santé pour obtenir des conseils personnalisés."

def create_emergency_alert(patient, message, triage_result):
    """Create emergency alert in Firestore"""
    try:
        from app.services.firebase_service import FirebaseService
        from datetime import datetime
        
        firebase = FirebaseService()
        alerts_collection = firebase.get_collection('alerts')
        
        alert_data = {
            'username': session.get('user'),
            'patient': {
                'nom_prenom': patient.nom_prenom,
                'age': patient.age,
                'sexe': patient.sexe,
                'email': patient.email,
                'phone': patient.phone or '',
                'symptomes': message,
                'localisation': patient.address or 'Non spécifiée'
            },
            'emergency_level': 5,  # Maximum priority
            'status': 'processing',
            'created_at': datetime.utcnow().isoformat(),
            'source': 'medibot_triage',
            'triage_data': triage_result
        }
        
        alerts_collection.add(alert_data)
        print(f"Emergency alert created for {patient.nom_prenom}")
        
    except Exception as e:
        print(f"Error creating emergency alert: {str(e)}")