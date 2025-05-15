import pytest
from flask import Flask
from app.main import create_app
from app import db
from app.core.security import create_access_token
from app.models.user import User

@pytest.fixture(scope="function")
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "JWT_SECRET_KEY": "test-secret-key"
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope="function")
def client(app):
    return app.test_client()

@pytest.fixture(scope="function")
def test_user(app):
    with app.app_context():
        user = User(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
            is_admin=False
        )
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture(scope="function")
def test_admin(app):
    with app.app_context():
        admin = User(
            email="admin@example.com",
            username="admin",
            full_name="Admin User",
            hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        return admin

@pytest.fixture(scope="function")
def test_user_token(test_user):
    return create_access_token(identity=test_user.username)

@pytest.fixture(scope="function")
def test_admin_token(test_admin):
    return create_access_token(identity=test_admin.username) 