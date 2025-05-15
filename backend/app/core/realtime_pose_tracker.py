import cv2
import time
import numpy as np
from .pose_detection import PoseDetector

class RealtimePoseTracker:
    def __init__(self):
        self.pose_detector = PoseDetector()
        self.current_exercise = "squat"  # default exercise
        self.rep_count = 0
        self.start_time = None
        self.fps = 0
        self.frame_count = 0
        self.last_fps_update = time.time()
        
    def set_exercise(self, exercise):
        """Set the current exercise to track"""
        self.current_exercise = exercise
        self.rep_count = 0
        
    def calculate_fps(self):
        """Calculate and update FPS"""
        self.frame_count += 1
        current_time = time.time()
        if current_time - self.last_fps_update >= 1.0:
            self.fps = self.frame_count
            self.frame_count = 0
            self.last_fps_update = current_time
            
    def draw_feedback(self, frame, feedback, angles=None):
        """Draw feedback and metrics on the frame"""
        # Draw FPS
        cv2.putText(frame, f"FPS: {self.fps}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Draw current exercise
        cv2.putText(frame, f"Exercise: {self.current_exercise}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Draw rep count
        cv2.putText(frame, f"Reps: {self.rep_count}", (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Draw feedback
        if feedback["feedback"]:
            y_pos = 120
            for msg in feedback["feedback"]:
                cv2.putText(frame, msg, (10, y_pos),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                y_pos += 30
                
        # Draw angles if available
        if angles:
            y_pos = 180
            for joint, angle in angles.items():
                cv2.putText(frame, f"{joint}: {angle:.1f}°", (10, y_pos),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                y_pos += 30
                
    def run(self):
        """Run the real-time pose tracking system"""
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Error: Could not open camera")
            return
            
        print("Press 'q' to quit")
        print("Press '1' for Squat")
        print("Press '2' for Plank")
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            # Calculate FPS
            self.calculate_fps()
            
            # Process frame
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            landmarks = self.pose_detector.detect_landmarks(rgb_frame)
            
            if landmarks:
                # Get feedback and angles
                feedback = self.pose_detector.validate_form(landmarks, self.current_exercise)
                angles = self.pose_detector.calculate_angles(landmarks)
                
                # Update rep count if exercise is completed
                if feedback.get("rep_completed", False):
                    self.rep_count += 1
                
                # Draw feedback and metrics
                self.draw_feedback(frame, feedback, angles)
                
                # Draw landmarks
                for landmark in landmarks:
                    x, y = int(landmark.x * frame.shape[1]), int(landmark.y * frame.shape[0])
                    cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
            
            # Display frame
            cv2.imshow('Real-Time Pose Tracking', frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('1'):
                self.set_exercise("squat")
            elif key == ord('2'):
                self.set_exercise("plank")
        
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    tracker = RealtimePoseTracker()
    tracker.run() 