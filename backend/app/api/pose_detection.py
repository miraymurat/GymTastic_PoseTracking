from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
import cv2
import numpy as np
import mediapipe as mp
from app.models.pose_detection import ExerciseFormChecker
import base64

pose_bp = Blueprint('pose', __name__)
form_checker = ExerciseFormChecker()

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

def calculate_angle(a, b, c):
    """Calculate the angle between three points"""
    a = np.array([a.x, a.y])
    b = np.array([b.x, b.y])
    c = np.array([c.x, c.y])
    
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    
    if angle > 180.0:
        angle = 360 - angle
    
    return angle

def check_squat_form(landmarks):
    """Check if the squat form is correct"""
    feedback = []
    incorrect_points = []
    is_correct = True

    # Get relevant landmarks
    hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
    knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
    ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
    shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]

    # Check knee angle
    knee_angle = calculate_angle(hip, knee, ankle)
    if knee_angle < 60 or knee_angle > 100:
        feedback.append("Bend your knees between 60-100 degrees")
        incorrect_points.extend([[knee.x, knee.y], [ankle.x, ankle.y]])
        is_correct = False

    # Check if knees are behind toes
    if knee.x > ankle.x:
        feedback.append("Keep your knees behind your toes")
        incorrect_points.extend([[knee.x, knee.y], [ankle.x, ankle.y]])
        is_correct = False

    # Check back angle
    back_angle = calculate_angle(shoulder, hip, knee)
    if back_angle < 45 or back_angle > 90:
        feedback.append("Keep your back straight")
        incorrect_points.extend([[shoulder.x, shoulder.y], [hip.x, hip.y]])
        is_correct = False

    return feedback, incorrect_points, is_correct

def check_plank_form(landmarks):
    """Check if the plank form is correct"""
    feedback = []
    incorrect_points = []
    is_correct = True

    # Get relevant landmarks
    shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
    hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
    ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
    
    # Check body alignment
    alignment_angle = calculate_angle(shoulder, hip, ankle)
    if alignment_angle < 160 or alignment_angle > 200:
        feedback.append("Keep your body in a straight line")
        incorrect_points.extend([[shoulder.x, shoulder.y], [hip.x, hip.y], [ankle.x, ankle.y]])
        is_correct = False
    
    # Check hip position
    if hip.y > shoulder.y + 0.1:
        feedback.append("Raise your hips")
        incorrect_points.extend([[hip.x, hip.y]])
        is_correct = False
    elif hip.y < shoulder.y - 0.1:
        feedback.append("Lower your hips")
        incorrect_points.extend([[hip.x, hip.y]])
        is_correct = False

    return feedback, incorrect_points, is_correct

@pose_bp.route('/analyze', methods=['POST'])
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
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame
        results = pose.process(rgb_frame)
        
        if not results.pose_landmarks:
            return jsonify({
                'feedback': ['No pose detected. Please make sure your full body is visible.'],
                'is_correct': False
            })
        
        # Convert landmarks to list for JSON serialization
        landmarks = []
        for landmark in results.pose_landmarks.landmark:
            landmarks.append({
                'x': landmark.x,
                'y': landmark.y,
                'z': landmark.z,
                'visibility': landmark.visibility
            })
        
        # Check form based on exercise type
        if exercise_type == 'squat':
            feedback, incorrect_points, is_correct = check_squat_form(results.pose_landmarks.landmark)
        elif exercise_type == 'plank':
            feedback, incorrect_points, is_correct = check_plank_form(results.pose_landmarks.landmark)
        else:
            feedback = ['Unsupported exercise type']
            incorrect_points = []
            is_correct = False
        
        return jsonify({
            'landmarks': landmarks,
            'feedback': feedback,
            'incorrect_points': incorrect_points,
            'is_correct': is_correct
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@pose_bp.route('/feedback', methods=['POST'])
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
        
        # Convert landmarks back to MediaPipe format
        mp_landmarks = []
        for landmark in landmarks:
            mp_landmark = mp.framework.formats.landmark_pb2.NormalizedLandmark()
            mp_landmark.x = landmark['x']
            mp_landmark.y = landmark['y']
            mp_landmark.z = landmark['z']
            mp_landmark.visibility = landmark['visibility']
            mp_landmarks.append(mp_landmark)
        
        # Check form based on exercise type
        if exercise_type == 'squat':
            feedback, incorrect_points, is_correct = check_squat_form(mp_landmarks)
        elif exercise_type == 'plank':
            feedback, incorrect_points, is_correct = check_plank_form(mp_landmarks)
        else:
            feedback = ['Unsupported exercise type']
            incorrect_points = []
            is_correct = False
        
        return jsonify({
            'feedback': feedback,
            'incorrect_points': incorrect_points,
            'is_correct': is_correct
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@pose_bp.route('/calibrate', methods=['POST'])
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
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame
        results = pose.process(rgb_frame)
        
        if not results.pose_landmarks:
            return jsonify({
                'error': 'No pose detected. Please make sure your full body is visible.'
            }), 400
        
        # Store calibration data
        form_checker.store_calibration(exercise_type, results.pose_landmarks.landmark)
        
        return jsonify({
            'message': 'Calibration successful'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500 