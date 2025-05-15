from app.models.base import BaseModel
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from email_validator import validate_email, EmailNotValidError

class User(BaseModel):
    __tablename__ = "users"

    email = db.Column(db.String(120), unique=True, index=True, nullable=False)
    username = db.Column(db.String(80), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    profile_picture = db.Column(db.String(200), nullable=True)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    google_id = db.Column(db.String(100), unique=True, nullable=True)
    has_profile = db.Column(db.Boolean, default=False)

    def __init__(self, **kwargs):
        if not kwargs.get('email'):
            raise ValueError("Email is required")
        if not kwargs.get('username'):
            raise ValueError("Username is required")
        if not kwargs.get('password'):
            raise ValueError("Password is required")
        
        # Validate email
        try:
            validate_email(kwargs['email'])
        except EmailNotValidError:
            raise ValueError("Invalid email format")
        
        # Set password
        self.set_password(kwargs.pop('password'))
        
        # Set other attributes
        for key, value in kwargs.items():
            setattr(self, key, value)

    def set_password(self, password):
        if not password:
            raise ValueError("Password cannot be empty")
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __str__(self):
        return self.username

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'full_name': self.full_name,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'profile_picture': self.profile_picture,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'has_profile': self.has_profile
        } 