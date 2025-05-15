import cv2
import numpy as np
import mediapipe as mp
from app.core.pose_detection import PoseDetector

def draw_landmarks(frame, landmarks, is_correct):
    """Draw body landmarks and connections on the frame, color based on correctness."""
    if landmarks is None:
        return frame
    
    h, w, _ = frame.shape
    color = (0, 255, 0) if is_correct else (0, 0, 255)
    
    # Only draw body (not face) landmarks: indices 11 and up
    body_indices = list(range(11, 33))
    for idx in body_indices:
        landmark = landmarks[idx]
        x = int(landmark['x'] * w)
        y = int(landmark['y'] * h)
        cv2.circle(frame, (x, y), 5, color, -1)
    
    # Draw body connections (no face)
    connections = [
        # Arms
        (11, 12), (11, 13), (13, 15), (12, 14), (14, 16),
        # Torso
        (11, 23), (12, 24), (23, 24),
        # Left leg
        (23, 25), (25, 27), (27, 29), (29, 31),
        # Right leg
        (24, 26), (26, 28), (28, 30), (30, 32)
    ]
    for start_idx, end_idx in connections:
        if 0 <= start_idx < len(landmarks) and 0 <= end_idx < len(landmarks):
            start_x = int(landmarks[start_idx]['x'] * w)
            start_y = int(landmarks[start_idx]['y'] * h)
            end_x = int(landmarks[end_idx]['x'] * w)
            end_y = int(landmarks[end_idx]['y'] * h)
            cv2.line(frame, (start_x, start_y), (end_x, end_y), color, 2)
    return frame

def show_exercise_selection():
    """Show exercise selection screen"""
    selection_window = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Add title
    cv2.putText(selection_window, "Select Exercise", (200, 100),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    # Add options
    cv2.putText(selection_window, "Press 'S' for Squat", (200, 200),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    cv2.putText(selection_window, "Press 'P' for Plank", (200, 300),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
    cv2.imshow('Exercise Selection', selection_window)
    
    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord('s'):
            cv2.destroyWindow('Exercise Selection')
            return "squat"
        elif key == ord('p'):
            cv2.destroyWindow('Exercise Selection')
            return "plank"
        elif key == ord('q'):
            return None

def main():
    # Initialize the pose detector
    detector = PoseDetector()
    
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    
    # Show exercise selection first
    current_exercise = show_exercise_selection()
    if current_exercise is None:
        cap.release()
        cv2.destroyAllWindows()
        return
    
    print(f"Selected exercise: {current_exercise}")
    print("Press 'q' to quit")
    print("Press 'r' to restart and select different exercise")
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break
            
        # Convert frame to RGB for pose detection
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        try:
            # Detect landmarks
            landmarks = detector.detect_landmarks(rgb_frame)
            
            # Validate form
            feedback = detector.validate_form(landmarks, current_exercise)
            is_correct = feedback.get('is_correct', False)
            
            # Draw landmarks and connections (color based on correctness)
            frame = draw_landmarks(frame, landmarks, is_correct)
            
            # Create a semi-transparent overlay for feedback
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (300, 150), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
            
            # Draw feedback on frame
            y_offset = 30
            cv2.putText(frame, f"Exercise: {current_exercise}", (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            for msg in feedback['feedback']:
                y_offset += 30
                color = (0, 255, 0) if msg == "Good form!" else (0, 0, 255)
                cv2.putText(frame, msg, (10, y_offset), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            
        except ValueError as e:
            # No pose detected
            cv2.putText(frame, "No pose detected", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Display the frame
        cv2.imshow('Pose Detection', frame)
        
        # Handle key presses
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            # Restart exercise selection
            current_exercise = show_exercise_selection()
            if current_exercise is None:
                break
    
    # Clean up
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main() 