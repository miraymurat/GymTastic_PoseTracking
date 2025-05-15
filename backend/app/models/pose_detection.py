import mediapipe as mp
import numpy as np
import cv2
from typing import Dict, List, Tuple, Optional

class PoseDetector:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5 
        )
        self.mp_drawing = mp.solutions.drawing_utils

    def detect_pose(self, image: np.ndarray) -> Optional[Dict[str, Tuple[float, float]]]:
        """Detect pose keypoints in the image using MediaPipe"""
        # Convert BGR to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.pose.process(image_rgb)
        
        if not results.pose_landmarks:
            return None
            
        landmarks = results.pose_landmarks.landmark
        keypoints = {}
        
        # Extract key points
        keypoints['left_shoulder'] = (landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER].x,
                                    landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER].y)
        keypoints['left_elbow'] = (landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW].x,
                                 landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW].y)
        keypoints['left_wrist'] = (landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST].x,
                                 landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST].y)
        keypoints['left_hip'] = (landmarks[self.mp_pose.PoseLandmark.LEFT_HIP].x,
                               landmarks[self.mp_pose.PoseLandmark.LEFT_HIP].y)
        keypoints['left_knee'] = (landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE].x,
                                landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE].y)
        keypoints['left_ankle'] = (landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE].x,
                                 landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE].y)
        
        # Add right side keypoints
        keypoints['right_shoulder'] = (landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER].x,
                                     landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER].y)
        keypoints['right_elbow'] = (landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW].x,
                                  landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW].y)
        keypoints['right_wrist'] = (landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST].x,
                                  landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST].y)
        keypoints['right_hip'] = (landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP].x,
                                landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP].y)
        keypoints['right_knee'] = (landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE].x,
                                 landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE].y)
        keypoints['right_ankle'] = (landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE].x,
                                  landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE].y)
        
        return keypoints

    def detect_exercise_type(self, keypoints: Dict[str, Tuple[float, float]]) -> Tuple[str, float]:
        """Detect if the person is doing a plank or squat"""
        # Calculate key angles for exercise classification
        hip_angle = self._calculate_angle(keypoints['left_shoulder'], 
                                        keypoints['left_hip'], 
                                        keypoints['left_knee'])
        knee_angle = self._calculate_angle(keypoints['left_hip'], 
                                         keypoints['left_knee'], 
                                         keypoints['left_ankle'])
        
        # Simple rule-based classification
        if hip_angle > 150 and knee_angle > 150:  # Body is straight
            return 'plank', 0.95
        elif hip_angle < 120 and knee_angle < 120:  # Body is bent
            return 'squat', 0.95
        else:
            return 'unknown', 0.5

    def _calculate_angle(self, point1: Tuple[float, float], 
                        point2: Tuple[float, float], 
                        point3: Tuple[float, float]) -> float:
        """Calculate angle between three points"""
        a = np.array(point1) - np.array(point2)
        b = np.array(point3) - np.array(point2)
        
        cos_angle = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        cos_angle = np.clip(cos_angle, -1.0, 1.0)
        angle = np.arccos(cos_angle)
        return np.degrees(angle)

class ExerciseFormChecker:
    def __init__(self):
        self.pose_detector = PoseDetector()
        self.exercise_standards = {
            'plank': {
                'correct_angles': {
                    'shoulder': (80, 100),  # degrees
                    'elbow': (90, 110),
                    'hip': (170, 190),
                    'knee': (170, 190)
                }
            },
            'squat': {
                'correct_angles': {
                    'hip': (80, 100),
                    'knee': (80, 100),
                    'ankle': (80, 100)
                }
            }
        }
    
    def check_plank_form(self, keypoints: Dict[str, Tuple[float, float]]) -> List[str]:
        """Check if plank form is correct based on keypoints"""
        feedback = []
        
        # Check shoulder angle
        shoulder_angle = self._calculate_angle(keypoints['left_shoulder'], 
                                            keypoints['left_elbow'], 
                                            keypoints['left_wrist'])
        if not self._is_angle_in_range(shoulder_angle, self.exercise_standards['plank']['correct_angles']['shoulder']):
            feedback.append("Keep your shoulders directly above your elbows")
            
        # Check hip alignment
        hip_angle = self._calculate_angle(keypoints['left_shoulder'], 
                                       keypoints['left_hip'], 
                                       keypoints['left_knee'])
        if not self._is_angle_in_range(hip_angle, self.exercise_standards['plank']['correct_angles']['hip']):
            feedback.append("Keep your body straight from shoulders to hips")
            
        return feedback
    
    def check_squat_form(self, keypoints: Dict[str, Tuple[float, float]]) -> List[str]:
        """Check if squat form is correct based on keypoints"""
        feedback = []
        
        # Check hip angle
        hip_angle = self._calculate_angle(keypoints['left_shoulder'], 
                                       keypoints['left_hip'], 
                                       keypoints['left_knee'])
        if not self._is_angle_in_range(hip_angle, self.exercise_standards['squat']['correct_angles']['hip']):
            feedback.append("Keep your back straight and chest up")
            
        # Check knee angle
        knee_angle = self._calculate_angle(keypoints['left_hip'], 
                                        keypoints['left_knee'], 
                                        keypoints['left_ankle'])
        if not self._is_angle_in_range(knee_angle, self.exercise_standards['squat']['correct_angles']['knee']):
            feedback.append("Keep your knees aligned with your toes")
            
        return feedback
    
    def _calculate_angle(self, point1: Tuple[float, float], 
                        point2: Tuple[float, float], 
                        point3: Tuple[float, float]) -> float:
        """Calculate angle between three points"""
        a = np.array(point1) - np.array(point2)
        b = np.array(point3) - np.array(point2)
        
        cos_angle = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        # Handle numerical instability
        cos_angle = np.clip(cos_angle, -1.0, 1.0)
        angle = np.arccos(cos_angle)
        return np.degrees(angle)
    
    def _is_angle_in_range(self, angle: float, angle_range: Tuple[float, float]) -> bool:
        """Check if angle is within specified range"""
        return angle_range[0] <= angle <= angle_range[1] 