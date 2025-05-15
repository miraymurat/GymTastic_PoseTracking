from functools import wraps
from flask import request, jsonify
import jwt
from datetime import datetime, timedelta
from app.config import Config
from app.utils.error_handler import AuthenticationError

def generate_token(user_id, role="user"):
    """Generate JWT token for user."""
    payload = {
        'id': user_id,
        'role': role,
        'exp': datetime.utcnow() + timedelta(days=1),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')

def token_required(f):
    """Decorator to require valid JWT token."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                raise AuthenticationError("Invalid token format")
        
        if not token:
            raise AuthenticationError("Token is missing")
        
        try:
            payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
            current_user = {
                'id': payload['id'],
                'role': payload.get('role', 'user')
            }
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.InvalidTokenError:
            raise AuthenticationError("Invalid token")
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def admin_required(f):
    """Decorator to require admin role."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                raise AuthenticationError("Invalid token format")
        
        if not token:
            raise AuthenticationError("Token is missing")
        
        try:
            payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
            if payload.get('role') != 'admin':
                raise AuthenticationError("Admin access required")
            current_user = {
                'id': payload['id'],
                'role': payload.get('role', 'user')
            }
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.InvalidTokenError:
            raise AuthenticationError("Invalid token")
        
        return f(current_user, *args, **kwargs)
    
    return decorated 