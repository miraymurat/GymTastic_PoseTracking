from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.core.pose_detection import PoseDetector
from app.core.exercise_instructions import ExerciseInstructions
import base64
import numpy as np
import cv2

pose_detection_bp = Blueprint('pose_detection', __name__)
pose_detector = PoseDetector()
exercise_instructions = ExerciseInstructions()

@pose_detection_bp.route('/analyze', methods=['POST'])
@jwt_required()
def analyze_pose():
    try:
        data = request.get_json()
        exercise_type = data.get('exercise_type')
        image_data = data.get('image')  # Base64 encoded image
        
        if not image_data or not exercise_type:
            return jsonify({
                'error': 'Missing image or exercise type'
            }), 400
        
        # Decode base64 image
        image_bytes = base64.b64decode(image_data.split(',')[1] if ',' in image_data else image_data)
        
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Process the image
        landmarks = pose_detector.detect_landmarks(frame)
        feedback = pose_detector.validate_form(landmarks, exercise_type)
        
        return jsonify({
            'landmarks': landmarks,
            'feedback': feedback['feedback'],
            'incorrect_points': feedback['incorrect_points'],
            'is_correct': feedback['is_correct']
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

@pose_detection_bp.route('/feedback', methods=['POST'])
@jwt_required()
def get_form_feedback():
    try:
        data = request.get_json()
        exercise_type = data.get('exercise_type')
        landmarks = data.get('landmarks')
        
        if not landmarks or not exercise_type:
            return jsonify({
                'error': 'Missing landmarks or exercise type'
            }), 400
        
        feedback = pose_detector.validate_form(landmarks, exercise_type)
        
        return jsonify({
            'feedback': feedback['feedback'],
            'incorrect_points': feedback['incorrect_points'],
            'is_correct': feedback['is_correct']
        }), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 400

@pose_detection_bp.route('/calibrate', methods=['POST'])
@jwt_required()
def calibrate_pose():
    try:
        data = request.get_json()
        exercise_type = data.get('exercise_type')
        image_data = data.get('image')
        
        if not image_data or not exercise_type:
            return jsonify({
                'error': 'Missing image or exercise type'
            }), 400
        
        # Decode base64 image
        image_bytes = base64.b64decode(image_data.split(',')[1] if ',' in image_data else image_data)
        
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Process the image
        landmarks = pose_detector.detect_landmarks(frame)
        pose_detector.store_calibration(exercise_type, landmarks)
        
        return jsonify({
            'message': 'Calibration successful'
        }), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 400

@pose_detection_bp.route('/instructions/<exercise>', methods=['GET'])
@jwt_required()
def get_exercise_instructions(exercise):
    try:
        instructions = exercise_instructions.get_instructions(exercise)
        return jsonify(instructions), 200
    except ValueError as e:
        return jsonify({'message': str(e)}), 404 