from app.models.base import BaseModel
from app import db
from datetime import datetime

class CompletedExercise(BaseModel):
    __tablename__ = "completed_exercises"

    workout_history_id = db.Column(db.Integer, db.ForeignKey("workout_history.id", ondelete="CASCADE"))
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercises.id", ondelete="CASCADE"))
    sets_completed = db.Column(db.Integer)
    reps_completed = db.Column(db.Integer)
    duration = db.Column(db.Integer)  # in seconds
    weight = db.Column(db.Float)  # in kg
    notes = db.Column(db.Text)

    # Relationships
    workout_history = db.relationship("WorkoutHistory", back_populates="completed_exercises")
    exercise = db.relationship("Exercise")

    def __init__(self, **kwargs):
        if not kwargs.get('exercise_id'):
            raise ValueError("Exercise ID is required")
        if not kwargs.get('sets_completed') and not kwargs.get('duration'):
            raise ValueError("Either sets or duration must be provided")
        super().__init__(**kwargs)

    def __str__(self):
        return f"Completed Exercise {self.id}"

    def to_dict(self):
        return {
            'id': self.id,
            'workout_history_id': self.workout_history_id,
            'exercise_id': self.exercise_id,
            'sets_completed': self.sets_completed,
            'reps_completed': self.reps_completed,
            'duration': self.duration,
            'weight': self.weight,
            'notes': self.notes,
            'exercise': self.exercise.to_dict() if self.exercise else None
        }

class WorkoutHistory(BaseModel):
    __tablename__ = "workout_history"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))
    workout_id = db.Column(db.Integer, db.ForeignKey("workouts.id", ondelete="CASCADE"))
    completed_at = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer)  # in minutes
    calories_burned = db.Column(db.Float)
    notes = db.Column(db.Text)
    rating = db.Column(db.Integer)  

    # Relationships
    user = db.relationship("User", backref="workout_history")
    workout = db.relationship("Workout", back_populates="workout_history")
    completed_exercises = db.relationship("CompletedExercise", back_populates="workout_history", cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        if not kwargs.get('user_id'):
            raise ValueError("User ID is required")
        if not kwargs.get('workout_id'):
            raise ValueError("Workout ID is required")
        if not kwargs.get('completed_at'):
            kwargs['completed_at'] = datetime.utcnow()
        super().__init__(**kwargs)

    def __str__(self):
        return f"Workout History {self.id}"

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'workout_id': self.workout_id,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration': self.duration,
            'calories_burned': self.calories_burned,
            'notes': self.notes,
            'rating': self.rating,
            'workout': self.workout.to_dict() if self.workout else None,
            'completed_exercises': [ex.to_dict() for ex in self.completed_exercises],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 