from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app import db
from app.core.security import get_password_hash

user_bp = Blueprint('user', __name__)

@user_bp.route('/', methods=['POST'])
def create_user():
    data = request.get_json()
    if db.session.query(User).filter(User.email == data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    hashed_password = get_password_hash(data['password'])
    user = User(
        email=data['email'],
        username=data['username'],
        hashed_password=hashed_password,
        full_name=data['full_name']
    )
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201

@user_bp.route('/me', methods=['GET'])
@jwt_required()
def read_users_me():
    current_username = get_jwt_identity()
    user = User.query.filter_by(username=current_username).first()
    return jsonify(user.to_dict())

@user_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_user_me():
    current_username = get_jwt_identity()
    user = User.query.filter_by(username=current_username).first()
    data = request.get_json()
    
    if data.get('email') and data['email'] != user.email:
        if db.session.query(User).filter(User.email == data['email']).first():
            return jsonify({'error': 'Email already registered'}), 400
        user.email = data['email']
    
    if data.get('username') and data['username'] != user.username:
        if db.session.query(User).filter(User.username == data['username']).first():
            return jsonify({'error': 'Username already taken'}), 400
        user.username = data['username']
    
    if data.get('full_name'):
        user.full_name = data['full_name']
    
    if data.get('password'):
        user.hashed_password = get_password_hash(data['password'])
    
    db.session.commit()
    return jsonify(user.to_dict()) 