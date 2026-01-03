from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app.services.firebase_service import FirebaseService
from firebase_admin import auth

class User:
    def __init__(self, username, email, password_hash, role='user', created_at=None, firebase_uid=None):
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.firebase_uid = firebase_uid
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'role': self.role,
            'created_at': self.created_at,
            'firebase_uid': self.firebase_uid
        }
    
    @staticmethod
    def from_dict(data):
        # Handle cases where fields might be missing
        email = data.get('email', '')
        username = data.get('username', email.split('@')[0] if email else 'unknown')
        return User(
            username=username,
            email=email,
            password_hash=data.get('password_hash', ''),
            role=data.get('role', 'patient'),
            created_at=data.get('created_at'),
            firebase_uid=data.get('firebase_uid')
        )

class UserStore:
    def __init__(self):
        self.firebase = FirebaseService()
        self.collection = self.firebase.get_collection('users')
    
    def create_user(self, username, email, password, role='patient'):
        try:
            # Step 1: Create user in Firebase Auth
            user_record = auth.create_user(
                email=email,
                password=password,
                display_name=username
            )
            firebase_uid = user_record.uid
            
            # Step 2: Create user in Firestore using Firebase UID
            password_hash = generate_password_hash(password)
            user = User(username, email, password_hash, role)
            user_data = user.to_dict()
            user_data['firebase_uid'] = firebase_uid
            
            self.collection.document(username).set(user_data)
            return user
            
        except auth.EmailAlreadyExistsError:
            return None
        except Exception as e:
            print(f'Error creating user: {e}')
            return None
    
    def get_user(self, username):
        doc = self.collection.document(username).get()
        if doc.exists:
            return User.from_dict(doc.to_dict())
        return None
    
    def authenticate(self, username, password):
        user = self.get_user(username)
        if user and user.check_password(password):
            return user
        return None
    
    def get_all_users(self):
        docs = self.collection.stream()
        return [User.from_dict(doc.to_dict()) for doc in docs]
    
    def update_user_role(self, username, new_role):
        doc_ref = self.collection.document(username)
        if doc_ref.get().exists:
            doc_ref.update({'role': new_role})
            return True
        return False
    
    def delete_user(self, username):
        doc_ref = self.collection.document(username)
        if doc_ref.get().exists:
            doc_ref.delete()
            return True
        return False
