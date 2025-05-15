import pytest
from flask import json

def test_create_exercise(client, test_admin_token):
    response = client.post(
        "/exercise",
        data=json.dumps({
            "name": "Push-up",
            "description": "A basic push-up exercise",
            "muscle_groups": ["chest", "triceps"],
            "difficulty": "beginner",
            "equipment": ["none"],
            "instructions": "Start in plank position...",
            "category": "bodyweight"
        }),
        content_type='application/json',
        headers={"Authorization": f"Bearer {test_admin_token}"}
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["name"] == "Push-up"
    assert data["difficulty"] == "beginner"
    assert "id" in data

def test_create_exercise_unauthorized(client, test_user_token):
    response = client.post(
        "/exercise",
        data=json.dumps({
            "name": "Push-up",
            "description": "A basic push-up exercise",
            "muscle_groups": ["chest", "triceps"],
            "difficulty": "beginner",
            "equipment": ["none"],
            "instructions": "Start in plank position...",
            "category": "bodyweight"
        }),
        content_type='application/json',
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 403
    data = json.loads(response.data)
    assert "error" in data

def test_get_exercises(client, test_admin_token):
    # First create an exercise
    client.post(
        "/exercise",
        data=json.dumps({
            "name": "Push-up",
            "description": "A basic push-up exercise",
            "muscle_groups": ["chest", "triceps"],
            "difficulty": "beginner",
            "equipment": ["none"],
            "instructions": "Start in plank position...",
            "category": "bodyweight"
        }),
        content_type='application/json',
        headers={"Authorization": f"Bearer {test_admin_token}"}
    )
    
    # Then get all exercises with pagination
    response = client.get("/exercise?skip=0&limit=10")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) > 0
    assert data[0]["name"] == "Push-up"

def test_get_exercise_by_id(client, test_admin_token):
    # First create an exercise
    create_response = client.post(
        "/exercise",
        data=json.dumps({
            "name": "Push-up",
            "description": "A basic push-up exercise",
            "muscle_groups": ["chest", "triceps"],
            "difficulty": "beginner",
            "equipment": ["none"],
            "instructions": "Start in plank position...",
            "category": "bodyweight"
        }),
        content_type='application/json',
        headers={"Authorization": f"Bearer {test_admin_token}"}
    )
    exercise_id = json.loads(create_response.data)["id"]
    
    # Then get the exercise by ID
    response = client.get(f"/exercise/{exercise_id}")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["name"] == "Push-up"
    assert data["id"] == exercise_id

def test_update_exercise(client, test_admin_token):
    # First create an exercise
    create_response = client.post(
        "/exercise",
        data=json.dumps({
            "name": "Push-up",
            "description": "A basic push-up exercise",
            "muscle_groups": ["chest", "triceps"],
            "difficulty": "beginner",
            "equipment": ["none"],
            "instructions": "Start in plank position...",
            "category": "bodyweight"
        }),
        content_type='application/json',
        headers={"Authorization": f"Bearer {test_admin_token}"}
    )
    exercise_id = json.loads(create_response.data)["id"]
    
    # Then update the exercise
    response = client.put(
        f"/exercise/{exercise_id}",
        data=json.dumps({
            "name": "Modified Push-up",
            "difficulty": "intermediate"
        }),
        content_type='application/json',
        headers={"Authorization": f"Bearer {test_admin_token}"}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["name"] == "Modified Push-up"
    assert data["difficulty"] == "intermediate"

def test_update_exercise_unauthorized(client, test_user_token):
    response = client.put(
        "/exercise/1",
        data=json.dumps({
            "name": "Modified Push-up",
            "difficulty": "intermediate"
        }),
        content_type='application/json',
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 403
    data = json.loads(response.data)
    assert "error" in data

def test_delete_exercise(client, test_admin_token):
    # First create an exercise
    create_response = client.post(
        "/exercise",
        data=json.dumps({
            "name": "Push-up",
            "description": "A basic push-up exercise",
            "muscle_groups": ["chest", "triceps"],
            "difficulty": "beginner",
            "equipment": ["none"],
            "instructions": "Start in plank position...",
            "category": "bodyweight"
        }),
        content_type='application/json',
        headers={"Authorization": f"Bearer {test_admin_token}"}
    )
    exercise_id = json.loads(create_response.data)["id"]
    
    # Then delete the exercise
    response = client.delete(
        f"/exercise/{exercise_id}",
        headers={"Authorization": f"Bearer {test_admin_token}"}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "message" in data
    assert data["message"] == "Exercise deleted successfully"

def test_delete_exercise_unauthorized(client, test_user_token):
    response = client.delete(
        "/exercise/1",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 403
    data = json.loads(response.data)
    assert "error" in data

def test_get_categories(client, test_admin_token):
    # First create exercises with different categories
    categories = ["bodyweight", "strength", "cardio"]
    for category in categories:
        client.post(
            "/exercise",
            data=json.dumps({
                "name": f"Test {category}",
                "description": "Test exercise",
                "muscle_groups": ["test"],
                "difficulty": "beginner",
                "equipment": ["none"],
                "instructions": "Test instructions",
                "category": category
            }),
            content_type='application/json',
            headers={"Authorization": f"Bearer {test_admin_token}"}
        )
    
    # Then get all categories
    response = client.get("/exercise/categories")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) >= len(categories)
    for category in categories:
        assert category in data 