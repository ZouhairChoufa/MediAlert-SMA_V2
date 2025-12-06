from flask import Blueprint, request, jsonify
from groq import Groq
from app.config import Config

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat', methods=['POST'])
def medibot_chat():
    """MediBot conversation endpoint"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Initialize Groq client
        client = Groq(api_key=Config.GROQ_API_KEY)
        
        # System prompt for medical assistant
        system_prompt = """Tu es MediBot, un assistant médical d'urgence intelligent. 
        
        RÈGLES IMPORTANTES:
        1. Tu ne remplaces JAMAIS un médecin
        2. En cas de symptômes graves, tu recommandes d'appeler le 15
        3. Tu donnes des conseils généraux de premiers secours
        4. Tu es rassurant mais prudent
        5. Tu réponds en français
        
        SYMPTÔMES D'URGENCE (rediriger vers alerte):
        - Douleur thoracique
        - Difficulté à respirer
        - Perte de conscience
        - Saignements importants
        - Douleur abdominale sévère
        
        Réponds de manière concise et professionnelle."""
        
        # Call Groq API
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            model=Config.GROQ_MODEL,
            temperature=0.3,
            max_tokens=200
        )
        
        response = chat_completion.choices[0].message.content
        
        return jsonify({
            'response': response,
            'timestamp': '2024-01-15T12:00:00Z'
        })
        
    except Exception as e:
        return jsonify({
            'response': 'Désolé, je rencontre un problème technique. En cas d\'urgence, appelez le 15.',
            'error': str(e)
        }), 500