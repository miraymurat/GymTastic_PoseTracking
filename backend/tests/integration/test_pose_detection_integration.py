import pytest
from flask import json
import base64
import os
import cv2
from app.core.pose_detection import PoseDetector

def test_analyze_pose(client, test_user_token):
    # Create a test image
    test_image_path = "test_image.jpg"
    with open(test_image_path, "wb") as f:
        f.write(b"test image data")
    
    # Read and encode the image
    with open(test_image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    # Clean up test image
    os.remove(test_image_path)
    
    response = client.post(
        "/api/pose/analyze",
        data=json.dumps({
            "image": image_data
        }),
        content_type='application/json',
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "exercise" in data
    assert "form_feedback" in data
    assert "landmarks" in data

def test_get_form_feedback(client, test_user_token):
    # Create a test image
    test_image_path = "test_image.jpg"
    with open(test_image_path, "wb") as f:
        f.write(b"test image data")
    
    # Read and encode the image
    with open(test_image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    # Clean up test image
    os.remove(test_image_path)
    
    response = client.post(
        "/api/pose/feedback",
        data=json.dumps({
            "image": image_data,
            "exercise": "push-up"
        }),
        content_type='application/json',
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "form_feedback" in data
    assert "landmarks" in data
    assert "angles" in data

def test_calibrate_pose(client, test_user_token):
    # Create a test image
    test_image_path = "test_image.jpg"
    with open(test_image_path, "wb") as f:
        f.write(b"test image data")
    
    # Read and encode the image
    with open(test_image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    # Clean up test image
    os.remove(test_image_path)
    
    response = client.post(
        "/api/pose/calibrate",
        data=json.dumps({
            "image": image_data,
            "exercise": "push-up"
        }),
        content_type='application/json',
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "calibration_data" in data
    assert "reference_angles" in data
    assert "reference_landmarks" in data

def test_get_exercise_instructions(client, test_user_token):
    response = client.get(
        "/api/pose/instructions/push-up",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "steps" in data
    assert "tips" in data
    assert "common_mistakes" in data

def test_analyze_pose_invalid_image(client, test_user_token):
    response = client.post(
        "/api/pose/analyze",
        data=json.dumps({
            "image": "invalid_base64_data"
        }),
        content_type='application/json',
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data

def test_get_form_feedback_invalid_exercise(client, test_user_token):
    # Create a test image
    test_image_path = "test_image.jpg"
    with open(test_image_path, "wb") as f:
        f.write(b"test image data")
    
    # Read and encode the image
    with open(test_image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    # Clean up test image
    os.remove(test_image_path)
    
    response = client.post(
        "/api/pose/feedback",
        data=json.dumps({
            "image": image_data,
            "exercise": "invalid_exercise"
        }),
        content_type='application/json',
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data

def test_calibrate_pose_invalid_exercise(client, test_user_token):
    # Create a test image
    test_image_path = "test_image.jpg"
    with open(test_image_path, "wb") as f:
        f.write(b"test image data")
    
    # Read and encode the image
    with open(test_image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    # Clean up test image
    os.remove(test_image_path)
    
    response = client.post(
        "/api/pose/calibrate",
        data=json.dumps({
            "image": image_data,
            "exercise": "invalid_exercise"
        }),
        content_type='application/json',
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data

def test_get_exercise_instructions_invalid_exercise(client, test_user_token):
    response = client.get(
        "/api/pose/instructions/invalid_exercise",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 404
    data = json.loads(response.data)
    assert "error" in data

def run_realtime_pose_tracking():
    cap = cv2.VideoCapture(0)  # 0 = default webcam
    pose_detector = PoseDetector()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        landmarks = pose_detector.detect_landmarks(rgb_frame)
        feedback = pose_detector.validate_form(landmarks, "squat")  # or "plank"

        # Display feedback on the frame
        if feedback["feedback"]:
            cv2.putText(frame, feedback["feedback"][0], (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.imshow('Real-Time Pose Tracking', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_realtime_pose_tracking() 