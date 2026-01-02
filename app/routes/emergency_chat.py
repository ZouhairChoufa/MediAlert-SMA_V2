from flask import Blueprint, request, jsonify, session
from groq import Groq
import json
from datetime import datetime
from app.decorators import login_required
from app.models.patient import PatientStore
from app.services.infermedica_service import InfermedicaService
from app.services.firebase_service import FirebaseService
from app.config_settings import Config

emergency_chat_bp = Blueprint('emergency_chat', __name__)
patient_store = PatientStore()
infermedica = InfermedicaService()
firebase = FirebaseService()

# Initialize Groq client
groq_client = Groq(api_key=Config.GROQ_API_KEY)

@emergency_chat_bp.route('/api/chat/emergency', methods=['POST'])
@login_required
def emergency_chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get patient profile
        username = session.get('user')
        patient = patient_store.get_profile(username)
        
        if not patient:
            return jsonify({
                'response': "🚨 URGENCE: Veuillez créer votre profil patient immédiatement pour que je puisse vous aider efficacement.",
                'needs_profile': True
            })
        
        # Step 1: Rapid Assessment (Groq Phase 1)
        symptoms = extract_emergency_symptoms(user_message)
        
        if not symptoms:
            return jsonify({
                'response': "Décrivez précisément vos symptômes. Que ressentez-vous exactement maintenant?"
            })
        
        # Step 2: Clinical Triage (Infermedica API)
        triage_result = infermedica.get_triage(symptoms, patient.age, patient.sexe)
        
        if not triage_result:
            # Fallback to emergency protocol for any medical complaint
            emergency_keywords = ['douleur', 'mal', 'saigne', 'respir', 'coeur', 'tête', 'ventre', 'chest', 'pain', 'breath']
            is_potential_emergency = any(keyword in user_message.lower() for keyword in emergency_keywords)
            
            if is_potential_emergency:
                create_emergency_alert(patient, user_message, None)
                return jsonify({
                    'response': "🚨 Système médical indisponible. Par sécurité, j'ai déclenché une alerte d'urgence. Les secours arrivent. Restez calme et gardez votre téléphone allumé.",
                    'emergency_triggered': True
                })
            else:
                return jsonify({
                    'response': "Système médical temporairement indisponible. Si c'est une urgence, appelez le 15 immédiatement."
                })
        
        # Step 3: The "Red Button" Logic
        triage_level = triage_result.get('triage_level', '').lower()
        recommended_channel = triage_result.get('recommended_channel', '').lower()
        
        is_emergency = (triage_level == 'emergency' or recommended_channel == 'ambulance')
        ambulance_status = 'Not Needed'
        
        if is_emergency:
            create_emergency_alert(patient, user_message, triage_result)
            ambulance_status = 'Dispatched'
        
        # Step 4: Pre-Arrival Instructions (Groq Phase 2)
        emergency_response = generate_emergency_instructions(
            user_message, 
            triage_result, 
            ambulance_status,
            triage_level
        )
        
        return jsonify({
            'response': emergency_response,
            'emergency_triggered': is_emergency,
            'triage_level': triage_level,
            'ambulance_status': ambulance_status
        })
        
    except Exception as e:
        print(f"Emergency chat error: {str(e)}")
        # Emergency fallback
        username = session.get('user')
        patient = patient_store.get_profile(username)
        if patient:
            create_emergency_alert(patient, user_message, None)
        
        return jsonify({
            'response': "🚨 Erreur système. Par sécurité, j'ai déclenché une alerte d'urgence. Les secours arrivent.",
            'emergency_triggered': True
        })

def extract_emergency_symptoms(user_message):
    """Step 1: Rapid symptom extraction for emergency triage"""
    
    system_prompt = """Tu es un extracteur de symptômes d'urgence médicale.
    Analyse le message et extrais UNIQUEMENT les symptômes médicaux critiques.
    
    SYMPTÔMES D'URGENCE À IDENTIFIER:
    - chest_pain (douleur thoracique)
    - shortness_of_breath (essoufflement)
    - severe_bleeding (saignement sévère)
    - unconsciousness (perte de conscience)
    - severe_headache (mal de tête sévère)
    - difficulty_breathing (difficulté respiratoire)
    - severe_abdominal_pain (douleur abdominale sévère)
    - allergic_reaction (réaction allergique)
    - burns (brûlures)
    - fracture (fracture)
    
    RÉPONSE FORMAT JSON:
    [{"id": "s_21", "choice_id": "present", "source": "initial"}]
    
    Si aucun symptôme clair: retourne []"""
    
    try:
        response = groq_client.chat.completions.create(
            model=Config.GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"URGENCE: {user_message}"}
            ],
            temperature=0.1,
            max_tokens=200
        )
        
        result = response.choices[0].message.content.strip()
        
        # Parse JSON or create basic symptom
        try:
            return json.loads(result)
        except:
            # Fallback: create generic symptom for any emergency keywords
            emergency_keywords = ['douleur', 'mal', 'saigne', 'respir', 'coeur', 'tête', 'ventre']
            if any(keyword in user_message.lower() for keyword in emergency_keywords):
                return [{"id": "s_1963", "choice_id": "present", "source": "initial"}]  # Generic pain
            return []
            
    except Exception as e:
        print(f"Symptom extraction error: {str(e)}")
        return [{"id": "s_1963", "choice_id": "present", "source": "initial"}]  # Fallback

def generate_emergency_instructions(user_message, triage_result, ambulance_status, triage_level):
    """Step 4: Generate emergency response with pre-arrival instructions"""
    
    system_prompt = f"""You are MediBot, an Emergency Medical Dispatch Assistant.
Your goal is to stabilize the patient until the ambulance arrives.

**Current Context:**
- Triage Level: {triage_level}
- Ambulance Status: {ambulance_status}

**Directives:**
1. **If Ambulance is Dispatched:**
   - START IMMEDIATELY with: '🚨 I have triggered a Red Alert. An ambulance is being dispatched to your location.'
   - GIVE INSTRUCTIONS: Provide concise, step-by-step First Aid instructions relevant to the symptoms (e.g., 'Apply direct pressure to the wound', 'Keep the patient warm', 'Do not give them water').
   - TONE: Authoritative, calm, and directive. Short sentences.

2. **If Situation is Urgent but NOT Life-Threatening:**
   - Advise the user to go to the nearest emergency room.
   - Ask if they need help finding transportation.

3. **General Rules:**
   - NEVER say 'I am an AI, I cannot help.' You must provide standard First Aid protocols.
   - Do not waste time with pleasantries ('Hello, how are you?'). Go straight to the medical issue.
   
RESPOND IN FRENCH. Maximum 150 words."""
    
    try:
        response = groq_client.chat.completions.create(
            model=Config.GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Patient dit: '{user_message}'. Données médicales: {triage_result}"}
            ],
            temperature=0.3,
            max_tokens=300
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"Emergency instruction error: {str(e)}")
        if ambulance_status == 'Dispatched':
            return "🚨 J'ai déclenché une alerte rouge. Une ambulance arrive. Restez calme, ne bougez pas, et suivez mes instructions. Gardez votre téléphone allumé."
        else:
            return "Rendez-vous immédiatement aux urgences les plus proches. Votre situation nécessite une évaluation médicale urgente."

def create_emergency_alert(patient, message, triage_data):
    """Create high-priority emergency alert in Firestore"""
    try:
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
                'localisation': patient.address or 'Localisation à déterminer'
            },
            'emergency_level': 5,  # Maximum priority
            'status': 'processing',
            'created_at': datetime.utcnow().isoformat(),
            'source': 'medibot_emergency',
            'triage_data': triage_data,
            'alert_type': 'RED_ALERT'
        }
        
        # Add to Firestore
        doc_ref = alerts_collection.add(alert_data)
        print(f"🚨 RED ALERT created for {patient.nom_prenom} - ID: {doc_ref[1].id}")
        
        return True
        
    except Exception as e:
        print(f"CRITICAL ERROR creating emergency alert: {str(e)}")
        return False