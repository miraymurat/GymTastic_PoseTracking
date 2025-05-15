import pytest
from flask import json

def test_create_workout(client, test_user_token):
    response = client.post(
        "/workout",
        data=json.dumps({
            "name": "Full Body Workout",
            "description": "A complete full body workout",
            "exercises": [
                {
                    "exercise_id": 1,
                    "sets": 3,
                    "reps": 12,
                    "rest_time": 60
                }
            ],
            "difficulty": "beginner",
            "duration": 45,
            "category": "strength"
        }),
        content_type='application/json',
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["name"] == "Full Body Workout"
    assert data["difficulty"] == "beginner"
    assert "id" in data
    assert "created_by" in data

def test_get_workouts(client, test_user_token):
    # First create a workout
    client.post(
        "/workout",
        data=json.dumps({
            "name": "Full Body Workout",
            "description": "A complete full body workout",
            "exercises": [
                {
                    "exercise_id": 1,
                    "sets": 3,
                    "reps": 12,
                    "rest_time": 60
                }
            ],
            "difficulty": "beginner",
            "duration": 45,
            "category": "strength"
        }),
        content_type='application/json',
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    # Then get all workouts with pagination
    response = client.get("/workout?skip=0&limit=10", headers={"Authorization": f"Bearer {test_user_token}"})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) > 0
    assert data[0]["name"] == "Full Body Workout"

def test_get_workout_by_id(client, test_user_token):
    # First create a workout
    create_response = client.post(
        "/workout",
        data=json.dumps({
            "name": "Full Body Workout",
            "description": "A complete full body workout",
            "exercises": [
                {
                    "exercise_id": 1,
                    "sets": 3,
                    "reps": 12,
                    "rest_time": 60
                }
            ],
            "difficulty": "beginner",
            "duration": 45,
            "category": "strength"
        }),
        content_type='application/json',
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    workout_id = json.loads(create_response.data)["id"]
    
    # Then get the workout by ID
    response = client.get(f"/workout/{workout_id}", headers={"Authorization": f"Bearer {test_user_token}"})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["name"] == "Full Body Workout"
    assert data["id"] == workout_id

def test_update_workout(client, test_user_token):
    # First create a workout
    create_response = client.post(
        "/workout",
        data=json.dumps({
            "name": "Full Body Workout",
            "description": "A complete full body workout",
            "exercises": [
                {
                    "exercise_id": 1,
                    "sets": 3,
                    "reps": 12,
                    "rest_time": 60
                }
            ],
            "difficulty": "beginner",
            "duration": 45,
            "category": "strength"
        }),
        content_type='application/json',
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    workout_id = json.loads(create_response.data)["id"]
    
    # Then update the workout
    response = client.put(
        f"/workout/{workout_id}",
        data=json.dumps({
            "name": "Modified Full Body Workout",
            "difficulty": "intermediate"
        }),
        content_type='application/json',
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["name"] == "Modified Full Body Workout"
    assert data["difficulty"] == "intermediate"

def test_update_workout_unauthorized(client, test_user_token, test_admin_token):
    # First create a workout as admin
    create_response = client.post(
        "/workout",
        data=json.dumps({
            "name": "Admin Workout",
            "description": "An admin workout",
            "exercises": [
                {
                    "exercise_id": 1,
                    "sets": 3,
                    "reps": 12,
                    "rest_time": 60
                }
            ],
            "difficulty": "beginner",
            "duration": 45,
            "category": "strength"
        }),
        content_type='application/json',
        headers={"Authorization": f"Bearer {test_admin_token}"}
    )
    workout_id = json.loads(create_response.data)["id"]
    
    # Try to update as regular user
    response = client.put(
        f"/workout/{workout_id}",
        data=json.dumps({
            "name": "Modified Workout",
            "difficulty": "intermediate"
        }),
        content_type='application/json',
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 403
    data = json.loads(response.data)
    assert "error" in data

def test_delete_workout(client, test_user_token):
    # First create a workout
    create_response = client.post(
        "/workout",
        data=json.dumps({
            "name": "Full Body Workout",
            "description": "A complete full body workout",
            "exercises": [
                {
                    "exercise_id": 1,
                    "sets": 3,
                    "reps": 12,
                    "rest_time": 60
                }
            ],
            "difficulty": "beginner",
            "duration": 45,
            "category": "strength"
        }),
        content_type='application/json',
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    workout_id = json.loads(create_response.data)["id"]
    
    # Then delete the workout
    response = client.delete(
        f"/workout/{workout_id}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "message" in data
    assert data["message"] == "Workout deleted successfully"

def test_delete_workout_unauthorized(client, test_user_token, test_admin_token):
    # First create a workout as admin
    create_response = client.post(
        "/workout",
        data=json.dumps({
            "name": "Admin Workout",
            "description": "An admin workout",
            "exercises": [
                {
                    "exercise_id": 1,
                    "sets": 3,
                    "reps": 12,
                    "rest_time": 60
                }
            ],
            "difficulty": "beginner",
            "duration": 45,
            "category": "strength"
        }),
        content_type='application/json',
        headers={"Authorization": f"Bearer {test_admin_token}"}
    )
    workout_id = json.loads(create_response.data)["id"]
    
    # Try to delete as regular user
    response = client.delete(
        f"/workout/{workout_id}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 403
    data = json.loads(response.data)
    assert "error" in data

def test_get_recommended_workouts(client, test_user_token):
    # First create some workouts
    workouts = [
        {
            "name": "Beginner Workout",
            "description": "A beginner workout",
            "exercises": [
                {
                    "exercise_id": 1,
                    "sets": 3,
                    "reps": 12,
                    "rest_time": 60
                }
            ],
            "difficulty": "beginner",
            "duration": 30,
            "category": "strength"
        },
        {
            "name": "Intermediate Workout",
            "description": "An intermediate workout",
            "exercises": [
                {
                    "exercise_id": 1,
                    "sets": 4,
                    "reps": 10,
                    "rest_time": 45
                }
            ],
            "difficulty": "intermediate",
            "duration": 45,
            "category": "strength"
        }
    ]
    
    for workout in workouts:
        client.post(
            "/workout",
            data=json.dumps(workout),
            content_type='application/json',
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
    
    # Then get recommended workouts
    response = client.get("/workout/recommended", headers={"Authorization": f"Bearer {test_user_token}"})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) > 0
    # Verify that workouts are sorted by difficulty
    difficulties = [w["difficulty"] for w in data]
    assert difficulties == sorted(difficulties) 