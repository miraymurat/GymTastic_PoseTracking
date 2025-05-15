import mediapipe as mp
import numpy as np
from PIL import Image
import io
import cv2

class PoseDetector:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=2,
            min_detection_confidence=0.5
        )
        self.calibration_data = {}

    def detect_landmarks(self, image):
        """Detect pose landmarks in the image."""
        # Convert image to RGB if it's not already
        if isinstance(image, np.ndarray):
            if image.shape[2] == 3:  # BGR format
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        results = self.pose.process(image)
        if not results.pose_landmarks:
            raise ValueError("No pose detected in the image")
        
        landmarks = []
        for landmark in results.pose_landmarks.landmark:
            landmarks.append({
                'x': landmark.x,
                'y': landmark.y,
                'z': landmark.z,
                'visibility': landmark.visibility
            })
        return landmarks

    def identify_exercise(self, landmarks):
        """Identify the exercise being performed based on pose landmarks."""
        # Calculate angles
        hip_angle = self._calculate_hip_angle(landmarks)
        shoulder_angle = self._calculate_shoulder_angle(landmarks)
        
        # Identify exercise based on angles
        if hip_angle < 90 and shoulder_angle > 150:
            return "squat"
        elif hip_angle > 150 and shoulder_angle > 150:
            return "plank"
        else:
            return "unknown"

    def validate_form(self, landmarks, exercise_type):
        """Validate the form of the exercise being performed."""
        if exercise_type == "squat":
            return self._validate_squat(landmarks)
        elif exercise_type == "plank":
            return self._validate_plank(landmarks)
        else:
            return {
                'feedback': ["Exercise type not supported"],
                'incorrect_points': [],
                'is_correct': False
            }

    def _validate_squat(self, landmarks):
        """Validate squat form."""
        feedback = []
        incorrect_points = []
        
        # Calculate all relevant angles
        hip_angle = self._calculate_hip_angle(landmarks)
        shoulder_angle = self._calculate_shoulder_angle(landmarks)
        back_angle = self._calculate_back_angle(landmarks)
        
        # Check if the overall position is squat-like
        is_squat_like = (
            hip_angle < 150 and  # Hips are bent
            shoulder_angle > 150 and  # Arms are relatively straight
            back_angle > 30  # Back is not completely horizontal
        )
        
        if not is_squat_like:
            feedback.append("Not in squat position")
            incorrect_points.append("position")
            return {
                'feedback': feedback,
                'incorrect_points': incorrect_points,
                'is_correct': False
            }
        
        # If in squat-like position, give specific feedback
        if hip_angle > 120:
            feedback.append("Try going lower")
            incorrect_points.append("depth")
        
        if shoulder_angle < 150:
            feedback.append("Straighten your arms")
            incorrect_points.append("arms")
        
        if back_angle < 45:
            feedback.append("Keep your back straight")
            incorrect_points.append("back")
        
        return {
            'feedback': feedback if feedback else ["Good form!"],
            'incorrect_points': incorrect_points,
            'is_correct': len(incorrect_points) == 0
        }

    def _validate_plank(self, landmarks):
        """Validate plank form."""
        feedback = []
        incorrect_points = []
        
        # Check hip angle
        hip_angle = self._calculate_hip_angle(landmarks)
        if hip_angle < 150:
            feedback.append("Keep your hips up")
            incorrect_points.append("hips")
        
        # Check shoulder angle
        shoulder_angle = self._calculate_shoulder_angle(landmarks)
        if shoulder_angle < 150:
            feedback.append("Keep your shoulders straight")
            incorrect_points.append("shoulders")
        
        # Check elbow angle
        elbow_angle = self._calculate_elbow_angle(landmarks)
        if elbow_angle < 85 or elbow_angle > 95:
            feedback.append("Keep your elbows at 90 degrees")
            incorrect_points.append("elbows")
        
        return {
            'feedback': feedback if feedback else ["Good form!"],
            'incorrect_points': incorrect_points,
            'is_correct': len(incorrect_points) == 0
        }

    def store_calibration(self, exercise_type, landmarks):
        """Store calibration data for an exercise."""
        self.calibration_data[exercise_type] = landmarks

    def get_calibration(self, exercise_type):
        """Get calibration data for an exercise."""
        return self.calibration_data.get(exercise_type)

    def _calculate_hip_angle(self, landmarks):
        """Calculate the angle at the hip."""
        hip = landmarks[23]  # Left hip
        knee = landmarks[25]  # Left knee
        ankle = landmarks[27]  # Left ankle
        
        return self._calculate_angle(hip, knee, ankle)

    def _calculate_shoulder_angle(self, landmarks):
        """Calculate the angle at the shoulder."""
        shoulder = landmarks[11]  # Left shoulder
        elbow = landmarks[13]  # Left elbow
        wrist = landmarks[15]  # Left wrist
        
        return self._calculate_angle(shoulder, elbow, wrist)

    def _calculate_back_angle(self, landmarks):
        """Calculate the angle of the back."""
        shoulder = landmarks[11]  # Left shoulder
        hip = landmarks[23]  # Left hip
        knee = landmarks[25]  # Left knee
        
        return self._calculate_angle(shoulder, hip, knee)

    def _calculate_elbow_angle(self, landmarks):
        """Calculate the angle at the elbow."""
        shoulder = landmarks[11]  # Left shoulder
        elbow = landmarks[13]  # Left elbow
        wrist = landmarks[15]  # Left wrist
        
        return self._calculate_angle(shoulder, elbow, wrist)

    def _check_knee_alignment(self, landmarks):
        """Check if knees are aligned with toes."""
        hip = landmarks[23]  # Left hip
        knee = landmarks[25]  # Left knee
        ankle = landmarks[27]  # Left ankle
        
        # Calculate angle between vertical line and knee-ankle line
        angle = self._calculate_angle(hip, knee, ankle)
        return 85 <= angle <= 95

    def _calculate_angle(self, a, b, c):
        """Calculate the angle between three points."""
        # Handle dict, array, or object with .x/.y
        def to_xy(point):
            if isinstance(point, dict):
                return np.array([point['x'], point['y']])
            elif hasattr(point, 'x') and hasattr(point, 'y'):
                return np.array([point.x, point.y])
            else:
                return np.array([point[0], point[1]])
        a = to_xy(a)
        b = to_xy(b)
        c = to_xy(c)
        ba = a - b
        bc = c - b
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
        angle = np.arccos(cosine_angle)
        return np.degrees(angle)

    def _calculate_angles(self, landmarks):
        """Calculate all relevant angles for the pose."""
        angles = {}
        
        # Calculate shoulder angle
        shoulder = landmarks[11]  # Left shoulder
        elbow = landmarks[13]  # Left elbow
        wrist = landmarks[15]  # Left wrist
        angles['left_shoulder'] = self._calculate_angle(shoulder, elbow, wrist)
        
        # Calculate elbow angle
        angles['left_elbow'] = self._calculate_angle(shoulder, elbow, wrist)
        
        # Calculate hip angle
        hip = landmarks[23]  # Left hip
        knee = landmarks[25]  # Left knee
        ankle = landmarks[27]  # Left ankle
        angles['left_hip'] = self._calculate_angle(hip, knee, ankle)
        
        return angles 