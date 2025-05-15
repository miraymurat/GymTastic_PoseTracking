from app.models.base import BaseModel
from app import db

class Workout(BaseModel):
    __tablename__ = "workouts"

    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))
    difficulty = db.Column(db.String(20))  # beginner, intermediate, advanced
    duration = db.Column(db.Integer)  # in minutes
    is_public = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    user = db.relationship("User", backref="workouts")
    workout_exercises = db.relationship("WorkoutExercise", back_populates="workout", cascade="all, delete-orphan")
    workout_history = db.relationship("WorkoutHistory", back_populates="workout", cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        if not kwargs.get('name'):
            raise ValueError("Workout name is required")
        if not kwargs.get('user_id'):
            raise ValueError("User ID is required")
        if kwargs.get('difficulty') not in ['beginner', 'intermediate', 'advanced']:
            raise ValueError("Difficulty must be one of: beginner, intermediate, advanced")
        super().__init__(**kwargs)

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'user_id': self.user_id,
            'difficulty': self.difficulty,
            'duration': self.duration,
            'is_public': self.is_public,
            'is_active': self.is_active,
            'exercises': [we.to_dict() for we in self.workout_exercises],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 