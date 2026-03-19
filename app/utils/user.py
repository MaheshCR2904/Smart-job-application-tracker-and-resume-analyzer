from flask_login import UserMixin
from bson import ObjectId

class User(UserMixin):
    """User class for Flask-Login integration"""
    
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.email = user_data.get('email')
        self.username = user_data.get('username')
        self.password_hash = user_data.get('password_hash')
        self.created_at = user_data.get('created_at')
        self.is_admin = user_data.get('is_admin', False)
        self.is_hr = user_data.get('is_hr', False)
        # Flask-Login's is_active is used for login eligibility
        # All users are active by default
        self._is_active = user_data.get('is_active', True)
        
    @property
    def is_active(self):
        """Return whether the user is active"""
        return self._is_active
        
    @property
    def is_admin_user(self):
        """Return whether the user is an admin"""
        return self.is_admin
        
    @staticmethod
    def get_by_email(db, email):
        """Get user by email"""
        user_data = db.users.find_one({'email': email})
        if user_data:
            return User(user_data)
        return None
    
    @staticmethod
    def get_by_id(db, user_id):
        """Get user by ID"""
        try:
            user_data = db.users.find_one({'_id': ObjectId(user_id)})
            if user_data:
                return User(user_data)
        except Exception:
            pass
        return None
    
    @staticmethod
    def create(db, username, email, password_hash):
        """Create new user"""
        from datetime import datetime
        user_data = {
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'created_at': datetime.utcnow(),
            'is_active': True
        }
        result = db.users.insert_one(user_data)
        user_data['_id'] = result.inserted_id
        return User(user_data)
    
    def check_password(self, password_hash):
        """Check if password matches"""
        from flask_bcrypt import check_password_hash
        return check_password_hash(self.password_hash, password_hash)
    
    def get_id(self):
        """Return user ID as string"""
        return self.id
