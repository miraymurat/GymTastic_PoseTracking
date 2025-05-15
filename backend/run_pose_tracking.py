from app.core.realtime_pose_tracker import RealtimePoseTracker

def main():
    print("Starting Real-Time Pose Tracking System...")
    print("Make sure you have a webcam connected and proper lighting.")
    print("\nControls:")
    print("- Press '1' to track Squats")
    print("- Press '2' to track Planks")
    print("- Press 'q' to quit")
    
    tracker = RealtimePoseTracker()
    tracker.run()

if __name__ == "__main__":
    main() 