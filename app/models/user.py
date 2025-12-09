from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
import os

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
    def __init__(self, filepath='data/users.json'):
        self.filepath = filepath
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        if not os.path.exists(self.filepath):
            with open(self.filepath, 'w') as f:
                json.dump({}, f)
    
    def _load_users(self):
        with open(self.filepath, 'r') as f:
            data = json.load(f)
            return {k: User.from_dict(v) for k, v in data.items()}
    
    def _save_users(self, users):
        with open(self.filepath, 'w') as f:
            data = {k: v.to_dict() for k, v in users.items()}
            json.dump(data, f, indent=2)
    
    def create_user(self, username, email, password, role='user'):
        users = self._load_users()
        if username in users:
            return None
        
        password_hash = generate_password_hash(password)
        user = User(username, email, password_hash, role)
        users[username] = user
        self._save_users(users)
        return user
    
    def get_user(self, username):
        users = self._load_users()
        return users.get(username)
    
    def authenticate(self, username, password):
        user = self.get_user(username)
        if user and user.check_password(password):
            return user
        return None
