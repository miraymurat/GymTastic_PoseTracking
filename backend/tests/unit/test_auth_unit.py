import pytest
from flask import json
from unittest.mock import patch, MagicMock
from app.core.security import verify_password, create_access_token

def test_verify_password():
    # Test password verification
    hashed_password = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"  # "password"
    assert verify_password("password", hashed_password) == True
    assert verify_password("wrongpassword", hashed_password) == False

def test_create_access_token():
    # Test token creation
    token = create_access_token(identity="testuser")
    assert isinstance(token, str)
    assert len(token) > 0

def test_user_model_creation():
    from models.user import User
    user = User(
        email="test@example.com",
        username="testuser",
        password="password123"
    )
    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert user.check_password("password123")

def test_user_validation():
    from models.user import User
    with pytest.raises(ValueError):
        User(email="invalid-email", username="testuser", password="password123")
    with pytest.raises(ValueError):
        User(email="test@example.com", username="", password="password123")
    with pytest.raises(ValueError):
        User(email="test@example.com", username="testuser", password="")

def test_user_methods():
    from models.user import User
    user = User(
        email="test@example.com",
        username="testuser",
        password="password123"
    )
    assert str(user) == "testuser"
    user_dict = user.to_dict()
    assert user_dict["email"] == "test@example.com"
    assert user_dict["username"] == "testuser"
    assert "password" not in user_dict

def test_token_generation():
    from models.user import User
    user = User(
        email="test@example.com",
        username="testuser",
        password="password123"
    )
    token = user.generate_token()
    assert token is not None
    assert isinstance(token, str)

def test_password_hashing():
    from models.user import User
    user = User(
        email="test@example.com",
        username="testuser",
        password="password123"
    )
    assert user.check_password("password123")
    assert not user.check_password("wrongpassword") 