import pytest
from flask import json
from datetime import datetime, timedelta

def test_create_workout_history(client, test_user_token):
    response = client.post(
        "/workout-history",
        data=json.dumps({
            "workout_id": 1,
            "exercise_name": "Push-up",
            "sets": 3,
            "reps": 12,
            "duration": 30,
            "details": {
                "form_score": 85,
                "notes": "Good form overall"
            }
        }),
        content_type='application/json',
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["exercise_name"] == "Push-up"
    assert data["sets"] == 3
    assert data["reps"] == 12
    assert "id" in data
    assert "user_id" in data

def test_get_workout_history(client, test_user_token):
    # First create a workout history entry
    client.post(
        "/workout-history",
        data=json.dumps({
            "workout_id": 1,
            "exercise_name": "Push-up",
            "sets": 3,
            "reps": 12,
            "duration": 30,
            "details": {
                "form_score": 85,
                "notes": "Good form overall"
            }
        }),
        content_type='application/json',
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    # Then get workout history with date filtering
    response = client.get(
        "/workout-history?days=7",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) > 0
    assert data[0]["exercise_name"] == "Push-up"

def test_get_workout_detail(client, test_user_token):
    # First create a workout history entry
    create_response = client.post(
        "/workout-history",
        data=json.dumps({
            "workout_id": 1,
            "exercise_name": "Push-up",
            "sets": 3,
            "reps": 12,
            "duration": 30,
            "details": {
                "form_score": 85,
                "notes": "Good form overall"
            }
        }),
        content_type='application/json',
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    workout_id = json.loads(create_response.data)["id"]
    
    # Then get the workout detail
    response = client.get(
        f"/workout-history/{workout_id}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["exercise_name"] == "Push-up"
    assert data["id"] == workout_id
    assert "details" in data

def test_get_workout_detail_unauthorized(client, test_user_token, test_admin_token):
    # First create a workout history entry as admin
    create_response = client.post(
        "/workout-history",
        data=json.dumps({
            "workout_id": 1,
            "exercise_name": "Push-up",
            "sets": 3,
            "reps": 12,
            "duration": 30,
            "details": {
                "form_score": 85,
                "notes": "Good form overall"
            }
        }),
        content_type='application/json',
        headers={"Authorization": f"Bearer {test_admin_token}"}
    )
    workout_id = json.loads(create_response.data)["id"]
    
    # Try to get the workout detail as regular user
    response = client.get(
        f"/workout-history/{workout_id}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 403
    data = json.loads(response.data)
    assert "error" in data

def test_delete_workout(client, test_user_token):
    # First create a workout history entry
    create_response = client.post(
        "/workout-history",
        data=json.dumps({
            "workout_id": 1,
            "exercise_name": "Push-up",
            "sets": 3,
            "reps": 12,
            "duration": 30,
            "details": {
                "form_score": 85,
                "notes": "Good form overall"
            }
        }),
        content_type='application/json',
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    workout_id = json.loads(create_response.data)["id"]
    
    # Then delete the workout history entry
    response = client.delete(
        f"/workout-history/{workout_id}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "message" in data
    assert data["message"] == "Workout history deleted successfully"

def test_delete_workout_unauthorized(client, test_user_token, test_admin_token):
    # First create a workout history entry as admin
    create_response = client.post(
        "/workout-history",
        data=json.dumps({
            "workout_id": 1,
            "exercise_name": "Push-up",
            "sets": 3,
            "reps": 12,
            "duration": 30,
            "details": {
                "form_score": 85,
                "notes": "Good form overall"
            }
        }),
        content_type='application/json',
        headers={"Authorization": f"Bearer {test_admin_token}"}
    )
    workout_id = json.loads(create_response.data)["id"]
    
    # Try to delete as regular user
    response = client.delete(
        f"/workout-history/{workout_id}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 403
    data = json.loads(response.data)
    assert "error" in data

def test_get_workout_stats(client, test_user_token):
    # First create multiple workout history entries
    workouts = [
        {
            "workout_id": 1,
            "exercise_name": "Push-up",
            "sets": 3,
            "reps": 12,
            "duration": 30,
            "details": {
                "form_score": 85,
                "notes": "Good form overall"
            }
        },
        {
            "workout_id": 1,
            "exercise_name": "Squat",
            "sets": 4,
            "reps": 10,
            "duration": 45,
            "details": {
                "form_score": 90,
                "notes": "Excellent form"
            }
        }
    ]
    
    for workout in workouts:
        client.post(
            "/workout-history",
            data=json.dumps(workout),
            content_type='application/json',
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
    
    # Then get workout stats
    response = client.get(
        "/workout-history/stats",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "total_workouts" in data
    assert "total_duration" in data
    assert "total_sets" in data
    assert "total_reps" in data
    assert "most_common_exercises" in data 