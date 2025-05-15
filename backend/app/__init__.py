from flask import Flask
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from app.config import config
from app.db import db

# Initialize extensions
migrate = Migrate()
jwt = JWTManager()

# This file is intentionally left minimal to avoid conflicts with main.py 