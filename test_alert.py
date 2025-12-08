"""
Test script to run emergency alert from terminal without web interface
Usage: python test_alert.py
"""

import os
import sys
from dotenv import load_dotenv

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv('config/.env')

from app import create_app
from app.crew.crew_simple import MediAlertCrew

app = create_app()
app_context = app.app_context()
app_context.push()

def test_emergency_alert():
    """Run a test emergency alert"""
    
    test_inputs = {
        'nom_prenom': 'Zouhair Choufa',
        'age': 45,
        'sexe': 'M',
        'symptomes': 'Douleur thoracique intense, difficulté à respirer',
        'localisation': 'Sidi Moussa, Ecole Ihssane, El jadida, Maroc',
        'nv_urgence': 'Élevé'
    }
    
    print("\n[TEST] Lancement du test d'alerte d'urgence...\n")
    
    # Initialize crew
    crew = MediAlertCrew()
    
    # Execute emergency response
    results = crew.execute_emergency_response(test_inputs)
    
    # Check for errors
    if 'error' in results:
        print(f"\n[ERROR] Erreur: {results['error']}")
        return False
    
    print("\n[SUCCESS] Test termine avec succes!")
    return True

if __name__ == '__main__':
    try:
        success = test_emergency_alert()
        app_context.pop()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[WARNING] Test interrompu par l'utilisateur")
        app_context.pop()
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Erreur fatale: {e}")
        app_context.pop()
        sys.exit(1)
