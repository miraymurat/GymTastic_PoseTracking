from datetime import timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.orm import Session
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user
)
from app import db
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserResponse, GoogleAuthData, LoginResponse
from datetime import datetime
import functools
import cv2
from app.core.pose_detection import PoseDetector

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.hashed_password, password):
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

@auth_bp.route('/google-auth', methods=['POST'])
def google_auth():
    data = request.get_json()
    email = data.get('email')
    name = data.get('name')
    photo = data.get('photo')
    id_token = data.get('idToken')
    
    # Check if user exists with this email
    user = User.query.filter_by(email=email).first()
    is_new_user = False
    
    if not user:
        # Create new user
        is_new_user = True
        user = User(
            email=email,
            username=email.split('@')[0],  # Use email prefix as username
            full_name=name,
            profile_picture=photo,
            google_id=id_token,
            has_profile=False
        )
        db.session.add(user)
        db.session.commit()
    else:
        # Update existing user's Google info
        user.google_id = id_token
        user.profile_picture = photo
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
        'isNewUser': is_new_user
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
    hashed_password = generate_password_hash(data['password'])
    user = User(
        email=data['email'],
        username=data['username'],
        full_name=data['full_name'],
        hashed_password=hashed_password,
        has_profile=False
    )
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
        @functools.wraps(fn)
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

def process_video(video_path):
    cap = cv2.VideoCapture(video_path)
    pose_detector = PoseDetector()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Convert the frame to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detect landmarks
        landmarks = pose_detector.detect_landmarks(rgb_frame)

        # Validate form (assuming you have a method to validate form)
        feedback = pose_detector.validate_form(landmarks, "squat")  # or "plank"

        # Display feedback on the frame
        cv2.putText(frame, feedback["feedback"][0], (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Display the frame
        cv2.imshow('Pose Detection', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Example usage
video_path = 'path/to/your/video.mp4'
process_video(video_path) 