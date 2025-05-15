from flask import Flask, request, jsonify
from flask_cors import CORS
from app.core.pose_detection import PoseDetector
from app.core.user import UserManager
from app.utils.auth import token_required
from app.utils.error_handler import handle_error
from app.config import Config

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Initialize managers
pose_detector = PoseDetector()
user_manager = UserManager()

# Error handlers
@app.errorhandler(Exception)
def handle_exception(e):
    return handle_error(e)

# Auth endpoints
@app.route('/auth/register', methods=['POST'])
def register():
    try:
        data = request.json
        result = user_manager.register_user(
            data.get('username'),
            data.get('email'),
            data.get('password')
        )
        return jsonify(result), 201
    except Exception as e:
        return handle_error(e)

@app.route('/auth/login', methods=['POST'])
def login():
    try:
        data = request.json
        result = user_manager.login_user(
            data.get('email'),
            data.get('password')
        )
        return jsonify(result)
    except Exception as e:
        return handle_error(e)

# User endpoints
@app.route('/users/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    try:
        profile = user_manager.get_user_profile(current_user['id'])
        return jsonify(profile)
    except Exception as e:
        return handle_error(e)

# Pose detection endpoints
@app.route('/pose/detect', methods=['POST'])
@token_required
def detect_pose(current_user):
    try:
        frame = request.json.get('frame')
        landmarks = pose_detector.detect_landmarks(frame)
        return jsonify({"landmarks": landmarks})
    except Exception as e:
        return handle_error(e)

@app.route('/pose/validate', methods=['POST'])
@token_required
def validate_pose(current_user):
    try:
        data = request.json
        result = pose_detector.validate_form(
            data.get('exercise_type'),
            data.get('landmarks')
        )
        return jsonify(result)
    except Exception as e:
        return handle_error(e)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=Config.DEBUG) 