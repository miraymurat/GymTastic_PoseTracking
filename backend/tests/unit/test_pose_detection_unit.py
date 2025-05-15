import pytest
import cv2
import numpy as np
from app.core.pose_detection import PoseDetector

@pytest.fixture
def pose_detector():
    return PoseDetector()

@pytest.fixture
def mock_mediapipe_landmarks():
    """Create a mock MediaPipe pose landmarks object"""
    class MockLandmark:
        def __init__(self, x, y, z=0, visibility=1):
            self.x = x
            self.y = y
            self.z = z
            self.visibility = visibility

    # Create a list of 33 landmarks (MediaPipe Pose uses 33 points)
    landmarks = [MockLandmark(0.0, 0.0) for _ in range(33)]
    
    # Set key points for squat position
    landmarks[23] = MockLandmark(0.5, 0.5)  # Left hip
    landmarks[25] = MockLandmark(0.5, 0.7)  # Left knee
    landmarks[27] = MockLandmark(0.5, 0.9)  # Left ankle
    landmarks[24] = MockLandmark(0.5, 0.5)  # Right hip
    landmarks[26] = MockLandmark(0.5, 0.7)  # Right knee
    landmarks[28] = MockLandmark(0.5, 0.9)  # Right ankle
    
    return landmarks

def test_pose_detector_initialization(pose_detector):
    """Test if pose detector initializes correctly"""
    assert pose_detector is not None

def test_landmark_detection_in_video(pose_detector):
    """Test landmark detection in a video frame"""
    # Create a test image with a simple shape that might be detected as a pose
    test_image = np.zeros((480, 640, 3), dtype=np.uint8)
    # Draw a simple stick figure
    cv2.line(test_image, (320, 100), (320, 300), (255, 255, 255), 2)  # Body
    cv2.line(test_image, (320, 200), (270, 250), (255, 255, 255), 2)  # Left arm
    cv2.line(test_image, (320, 200), (370, 250), (255, 255, 255), 2)  # Right arm
    cv2.line(test_image, (320, 300), (270, 400), (255, 255, 255), 2)  # Left leg
    cv2.line(test_image, (320, 300), (370, 400), (255, 255, 255), 2)  # Right leg
    
    try:
        landmarks = pose_detector.detect_landmarks(test_image)
        assert landmarks is not None
    except ValueError:
        # It's okay if no pose is detected in the test image
        pass

def test_angle_calculation(pose_detector):
    """Test angle calculation between points"""
    # Create mock landmarks for testing angle calculation
    mock_landmarks = [
        type('Landmark', (), {'x': 0.5, 'y': 0.5})(),  # Center point
        type('Landmark', (), {'x': 0.4, 'y': 0.4})(),  # Point 1
        type('Landmark', (), {'x': 0.6, 'y': 0.6})()   # Point 2
    ]
    
    angle = pose_detector._calculate_angle(mock_landmarks[0], mock_landmarks[1], mock_landmarks[2])
    assert isinstance(angle, float)
    assert 0 <= angle <= 180

def test_squat_form_validation(pose_detector, mock_mediapipe_landmarks):
    """Test squat form validation"""
    feedback = pose_detector.validate_form(mock_mediapipe_landmarks, "squat")
    assert isinstance(feedback, dict)
    assert "feedback" in feedback
    assert isinstance(feedback["feedback"], list)

def test_plank_form_validation(pose_detector, mock_mediapipe_landmarks):
    """Test plank form validation"""
    # Modify landmarks for plank position
    mock_mediapipe_landmarks[11] = type('Landmark', (), {'x': 0.5, 'y': 0.3})()  # Left shoulder
    mock_mediapipe_landmarks[13] = type('Landmark', (), {'x': 0.5, 'y': 0.4})()  # Left elbow
    mock_mediapipe_landmarks[15] = type('Landmark', (), {'x': 0.5, 'y': 0.5})()  # Left wrist
    
    feedback = pose_detector.validate_form(mock_mediapipe_landmarks, "plank")
    assert isinstance(feedback, dict)
    assert "feedback" in feedback
    assert isinstance(feedback["feedback"], list)

def test_real_time_tracking(pose_detector):
    """Test real-time tracking functionality"""
    # Create a mock video capture
    cap = cv2.VideoCapture(0)
    assert cap.isOpened()
    
    try:
        # Read a frame
        ret, frame = cap.read()
        assert ret
        
        # Test pose detection on the frame
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        try:
            landmarks = pose_detector.detect_landmarks(rgb_frame)
            assert landmarks is not None
        except ValueError:
            # It's okay if no pose is detected in the test frame
            pass
    finally:
        # Clean up
        cap.release()

def test_exercise_switching(pose_detector):
    # Squat landmarks
    squat_landmarks = [type('Landmark', (), {'x': 0.0, 'y': 0.0})() for _ in range(33)]
    squat_landmarks[23] = type('Landmark', (), {'x': 0.5, 'y': 0.5})()
    squat_landmarks[25] = type('Landmark', (), {'x': 0.5, 'y': 0.7})()
    squat_landmarks[27] = type('Landmark', (), {'x': 0.5, 'y': 0.9})()
    squat_landmarks[24] = type('Landmark', (), {'x': 0.5, 'y': 0.5})()
    squat_landmarks[26] = type('Landmark', (), {'x': 0.5, 'y': 0.7})()
    squat_landmarks[28] = type('Landmark', (), {'x': 0.5, 'y': 0.9})()
    squat_feedback = pose_detector.validate_form(squat_landmarks, "squat")

    # Plank landmarks
    plank_landmarks = [type('Landmark', (), {'x': 0.0, 'y': 0.0})() for _ in range(33)]
    plank_landmarks[11] = type('Landmark', (), {'x': 0.5, 'y': 0.3})()
    plank_landmarks[13] = type('Landmark', (), {'x': 0.5, 'y': 0.4})()
    plank_landmarks[15] = type('Landmark', (), {'x': 0.5, 'y': 0.5})()
    plank_feedback = pose_detector.validate_form(plank_landmarks, "plank")

    assert squat_feedback != plank_feedback 