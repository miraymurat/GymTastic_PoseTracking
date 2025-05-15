from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models.user import User
from app import db
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({
            'error': 'Incorrect username or password'
        }), 401
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    access_token = create_access_token(
        identity=user.username,
        expires_delta=timedelta(minutes=30)
    )
    
    return jsonify({
        'access_token': access_token,
        'token_type': 'bearer',
        'user': user.to_dict(),
        'isNewUser': False
    })

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Check if username exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({
            'error': 'Username already registered'
        }), 400
    
    # Check if email exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({
            'error': 'Email already registered'
        }), 400
    
    # Create new user
    user = User(
        email=data['email'],
        username=data['username'],
        full_name=data['full_name'],
        has_profile=False
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify(user.to_dict())

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    current_username = get_jwt_identity()
    user = User.query.filter_by(username=current_username).first()
    return jsonify(user.to_dict())

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required()
def refresh():
    current_username = get_jwt_identity()
    access_token = create_access_token(
        identity=current_username,
        expires_delta=timedelta(minutes=30)
    )
    return jsonify({
        'access_token': access_token,
        'token_type': 'bearer'
    })

def admin_required():
    def decorator(fn):
        @jwt_required()
        def wrapper(*args, **kwargs):
            current_username = get_jwt_identity()
            user = User.query.filter_by(username=current_username).first()
            if not user or not user.is_admin:
                return jsonify({
                    'error': 'The user doesn\'t have enough privileges'
                }), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator 