"""
Models package initialization
"""
from app.models.user import User
from app.models.pose_detection import PoseDetection
from app.models.base import BaseModel

__all__ = ['User', 'PoseDetection', 'BaseModel'] 