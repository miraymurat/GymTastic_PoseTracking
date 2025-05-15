import pytest
from flask import json

def test_login_success(client, test_user):
    response = client.post(
        "/auth/login",
        data=json.dumps({
            "username": "testuser",
            "password": "password123"
        }),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"
    assert "user" in data
    assert "isNewUser" in data
    assert data["user"]["username"] == "testuser"

def test_login_wrong_credentials(client):
    response = client.post(
        "/auth/login",
        data=json.dumps({
            "username": "testuser",
            "password": "wrongpassword"
        }),
        content_type='application/json'
    )
    assert response.status_code == 401
    data = json.loads(response.data)
    assert "error" in data
    assert data["error"] == "Incorrect username or password"

def test_register_success(client):
    response = client.post(
        "/auth/register",
        data=json.dumps({
            "email": "new@example.com",
            "username": "newuser",
            "full_name": "New User",
            "password": "password123"
        }),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["email"] == "new@example.com"
    assert data["username"] == "newuser"
    assert data["full_name"] == "New User"
    assert "has_profile" in data
    assert data["has_profile"] == False

def test_register_existing_username(client, test_user):
    response = client.post(
        "/auth/register",
        data=json.dumps({
            "email": "different@example.com",
            "username": "testuser",  # Already exists
            "full_name": "Test User",
            "password": "password123"
        }),
        content_type='application/json'
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data
    assert data["error"] == "Username already registered"

def test_register_existing_email(client, test_user):
    response = client.post(
        "/auth/register",
        data=json.dumps({
            "email": "test@example.com",  # Already exists
            "username": "differentuser",
            "full_name": "Test User",
            "password": "password123"
        }),
        content_type='application/json'
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data
    assert data["error"] == "Email already registered"

def test_get_current_user(client, test_user_token):
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["username"] == "testuser"
    assert "email" in data
    assert "full_name" in data
    assert "has_profile" in data

def test_get_current_user_unauthorized(client):
    response = client.get("/auth/me")
    assert response.status_code == 401

def test_refresh_token(client, test_user_token):
    response = client.post(
        "/auth/refresh",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"

def test_refresh_token_unauthorized(client):
    response = client.post("/auth/refresh")
    assert response.status_code == 401

def test_google_auth_new_user(client):
    response = client.post(
        "/auth/google-auth",
        data=json.dumps({
            "email": "google@example.com",
            "name": "Google User",
            "photo": "https://example.com/photo.jpg",
            "idToken": "google-token-123"
        }),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["user"]["email"] == "google@example.com"
    assert data["isNewUser"] == True
    assert "access_token" in data

def test_google_auth_existing_user(client, test_user):
    response = client.post(
        "/auth/google-auth",
        data=json.dumps({
            "email": "test@example.com",  # Existing user
            "name": "Updated Name",
            "photo": "https://example.com/new-photo.jpg",
            "idToken": "google-token-123"
        }),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["user"]["email"] == "test@example.com"
    assert data["isNewUser"] == False
    assert "access_token" in data 