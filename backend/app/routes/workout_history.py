from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.workout_history import WorkoutHistory
from app.models.user import User
from app import db
from datetime import datetime, timedelta

workout_history_bp = Blueprint('workout_history', __name__)

@workout_history_bp.route('/', methods=['POST'])
@jwt_required()
def create_workout_history():
    current_username = get_jwt_identity()
    user = User.query.filter_by(username=current_username).first()
    
    data = request.get_json()
    workout = WorkoutHistory(
        user_id=user.id,
        exercise_name=data['exercise_name'],
        sets=data['sets'],
        reps=data['reps'],
        duration=data['duration'],
        details=data['details']
    )
    db.session.add(workout)
    db.session.commit()
    return jsonify(workout.to_dict()), 201

@workout_history_bp.route('/', methods=['GET'])
@jwt_required()
def get_workout_history():
    current_username = get_jwt_identity()
    user = User.query.filter_by(username=current_username).first()
    
    days = request.args.get('days', 30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    workouts = WorkoutHistory.query.filter_by(
        user_id=user.id
    ).filter(
        WorkoutHistory.date >= start_date
    ).order_by(
        WorkoutHistory.date.desc()
    ).all()
    
    return jsonify([workout.to_dict() for workout in workouts])

@workout_history_bp.route('/<int:workout_id>', methods=['GET'])
@jwt_required()
def get_workout_detail(workout_id):
    current_username = get_jwt_identity()
    user = User.query.filter_by(username=current_username).first()
    
    workout = WorkoutHistory.query.filter_by(
        id=workout_id,
        user_id=user.id
    ).first_or_404()
    
    return jsonify(workout.to_dict())

@workout_history_bp.route('/<int:workout_id>', methods=['DELETE'])
@jwt_required()
def delete_workout(workout_id):
    current_username = get_jwt_identity()
    user = User.query.filter_by(username=current_username).first()
    
    workout = WorkoutHistory.query.filter_by(
        id=workout_id,
        user_id=user.id
    ).first_or_404()
    
    db.session.delete(workout)
    db.session.commit()
    return jsonify({'message': 'Workout deleted successfully'})

@workout_history_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_workout_stats():
    current_username = get_jwt_identity()
    user = User.query.filter_by(username=current_username).first()
    
    # Get last 30 days of workouts
    start_date = datetime.utcnow() - timedelta(days=30)
    workouts = WorkoutHistory.query.filter_by(
        user_id=user.id
    ).filter(
        WorkoutHistory.date >= start_date
    ).all()
    
    # Calculate basic stats
    total_workouts = len(workouts)
    total_duration = sum(w.duration for w in workouts if w.duration)
    total_sets = sum(w.sets for w in workouts if w.sets)
    total_reps = sum(w.reps for w in workouts if w.reps)
    
    # Get most common exercises
    exercise_counts = {}
    for workout in workouts:
        exercise_counts[workout.exercise_name] = exercise_counts.get(workout.exercise_name, 0) + 1
    
    most_common = sorted(
        exercise_counts.items(),
        key=lambda x: x[1],
        reverse=True
    )[:5]
    
    return jsonify({
        'total_workouts': total_workouts,
        'total_duration': total_duration,
        'total_sets': total_sets,
        'total_reps': total_reps,
        'most_common_exercises': [
            {'exercise': name, 'count': count}
            for name, count in most_common
        ]
    }) 