from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.config import Config
from app.commands import register_commands
from app.db import db

# Initialize Flask extensions
jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)

    # Import models to ensure they are registered with SQLAlchemy
    from app.models.user import User
    from app.models.exercise import Exercise, WorkoutExercise
    from app.models.workout import Workout
    from app.models.workout_history import WorkoutHistory

    # Register CLI commands
    register_commands(app)

    # Register blueprints
    from app.api.auth import auth_bp
    from app.api.exercise import exercise_bp
    from app.api.workout import workout_bp
    from app.api.pose_detection import pose_bp
    from app.api.workout_history import workout_history_bp
    from app.api.user import user_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(exercise_bp, url_prefix='/api/exercises')
    app.register_blueprint(workout_bp, url_prefix='/api/workouts')
    app.register_blueprint(pose_bp, url_prefix='/api/pose')
    app.register_blueprint(workout_history_bp, url_prefix='/api/workout-history')
    app.register_blueprint(user_bp, url_prefix='/api/users')

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

    @app.route('/')
    def root():
        return jsonify({'message': 'Welcome to GymTastic API'})

    return app 