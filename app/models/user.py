from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app.services.firebase_service import FirebaseService

class User:
    def __init__(self, username, email, password_hash, role='user', created_at=None):
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.created_at = created_at or datetime.utcnow().isoformat()
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'role': self.role,
            'created_at': self.created_at
        }
    
    @staticmethod
    def from_dict(data):
        return User(
            username=data['username'],
            email=data['email'],
            password_hash=data['password_hash'],
            role=data.get('role', 'user'),
            created_at=data.get('created_at')
        )

class UserStore:
    def __init__(self):
        self.firebase = FirebaseService()
        self.collection = self.firebase.get_collection('users')
    
    def create_user(self, username, email, password, role='user'):
        if self.collection.document(username).get().exists:
            return None
        
        password_hash = generate_password_hash(password)
        user = User(username, email, password_hash, role)
        self.collection.document(username).set(user.to_dict())
        return user
    
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
