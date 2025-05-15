from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.workout import Workout
from app.models.user import User
from app import db

workout_bp = Blueprint('workout', __name__)

@workout_bp.route('/', methods=['POST'])
@jwt_required()
def create_workout():
    current_username = get_jwt_identity()
    user = User.query.filter_by(username=current_username).first()
    
    data = request.get_json()
    workout = Workout(
        **data,
        created_by=user.id
    )
    db.session.add(workout)
    db.session.commit()
    return jsonify(workout.to_dict()), 201

@workout_bp.route('/', methods=['GET'])
@jwt_required()
def get_workouts():
    current_username = get_jwt_identity()
    user = User.query.filter_by(username=current_username).first()
    
    skip = request.args.get('skip', 0, type=int)
    limit = request.args.get('limit', 100, type=int)
    
    workouts = Workout.query.filter_by(
        created_by=user.id
    ).offset(skip).limit(limit).all()
    
    return jsonify([workout.to_dict() for workout in workouts])

@workout_bp.route('/<int:workout_id>', methods=['GET'])
@jwt_required()
def get_workout(workout_id):
    current_username = get_jwt_identity()
    user = User.query.filter_by(username=current_username).first()
    
    workout = Workout.query.filter_by(
        id=workout_id,
        created_by=user.id
    ).first_or_404()
    
    return jsonify(workout.to_dict())

@workout_bp.route('/<int:workout_id>', methods=['PUT'])
@jwt_required()
def update_workout(workout_id):
    current_username = get_jwt_identity()
    user = User.query.filter_by(username=current_username).first()
    
    workout = Workout.query.filter_by(
        id=workout_id,
        created_by=user.id
    ).first_or_404()
    
    data = request.get_json()
    for key, value in data.items():
        setattr(workout, key, value)
    
    db.session.commit()
    return jsonify(workout.to_dict())

@workout_bp.route('/<int:workout_id>', methods=['DELETE'])
@jwt_required()
def delete_workout(workout_id):
    current_username = get_jwt_identity()
    user = User.query.filter_by(username=current_username).first()
    
    workout = Workout.query.filter_by(
        id=workout_id,
        created_by=user.id
    ).first_or_404()
    
    db.session.delete(workout)
    db.session.commit()
    return jsonify({'message': 'Workout deleted successfully'})

@workout_bp.route('/recommended', methods=['GET'])
@jwt_required()
def get_recommended_workouts():
    current_username = get_jwt_identity()
    user = User.query.filter_by(username=current_username).first()
    
    # Get user's workout history to determine preferences
    # This is a simple implementation - you might want to add more sophisticated logic
    workouts = Workout.query.filter(
        Workout.difficulty.in_(['beginner', 'intermediate'])
    ).limit(5).all()
    
    return jsonify([workout.to_dict() for workout in workouts]) 