import requests
import json
from app.config_settings import Config

class InfermedicaService:
    def __init__(self):
        self.app_id = Config.INFERMEDICA_APP_ID or '334a6295'
        self.app_key = Config.INFERMEDICA_APP_KEY or 'fd1d2acdab6b9159dad12d5ee83e3fbf'
        self.base_url = Config.INFERMEDICA_API_URL
        
        print(f"Infermedica credentials - App ID: {self.app_id}, App Key: {self.app_key[:10]}...")
        
        self.headers = {
            'App-Id': self.app_id,
            'App-Key': self.app_key,
            'Content-Type': 'application/json',
            'Model': 'infermedica-en'
        }
    
    def get_triage(self, symptoms_list, age, sex):
        """
        Get medical triage from Infermedica API
        
        Args:
            symptoms_list: List of symptom dictionaries with 'id' and 'choice_id'
            age: Patient age (integer)
            sex: Patient sex ('male' or 'female')
        
        Returns:
            dict: Triage response from Infermedica
        """
        try:
            payload = {
                "sex": sex.lower(),
                "age": {"value": age},
                "evidence": symptoms_list
            }
            
            print(f"Infermedica request - URL: {self.base_url}/triage")
            print(f"Infermedica request - Headers: {self.headers}")
            print(f"Infermedica request - Payload: {payload}")
            
            response = requests.post(
                f"{self.base_url}/triage",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Infermedica API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error calling Infermedica API: {str(e)}")
            return None
    
    def search_symptoms(self, query):
        """
        Search for symptoms in Infermedica database
        
        Args:
            query: Search query string
            
        Returns:
            list: List of matching symptoms
        """
        try:
            response = requests.get(
                f"{self.base_url}/symptoms",
                headers=self.headers,
                params={"phrase": query, "max_results": 5},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return []
                
        except Exception as e:
            print(f"Error searching symptoms: {str(e)}")
            return []