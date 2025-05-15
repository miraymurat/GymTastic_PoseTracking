import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

def test_workout_history_model_creation():
    from app.models.workout_history import WorkoutHistory
    workout_history = WorkoutHistory(
        workout_id=1,
        user_id=1,
        duration=45,
        notes="Great workout!"
    )
    assert workout_history.workout_id == 1
    assert workout_history.user_id == 1
    assert workout_history.duration == 45
    assert workout_history.notes == "Great workout!"

def test_workout_history_validation():
    from app.models.workout_history import WorkoutHistory
    with pytest.raises(ValueError):
        WorkoutHistory(workout_id=1, user_id=1, duration=-1)
    with pytest.raises(ValueError):
        WorkoutHistory(workout_id=1, user_id=1, duration=45, completed_at=None)

def test_workout_history_methods():
    from app.models.workout_history import WorkoutHistory
    workout_history = WorkoutHistory(
        workout_id=1,
        user_id=1,
        duration=45,
        notes="Great workout!"
    )
    assert str(workout_history) == f"Workout History {workout_history.id}"
    workout_history_dict = workout_history.to_dict()
    assert workout_history_dict["workout_id"] == 1
    assert workout_history_dict["user_id"] == 1
    assert workout_history_dict["duration"] == 45
    assert workout_history_dict["notes"] == "Great workout!"

def test_workout_history_relationship():
    from app.models.workout_history import WorkoutHistory
    from app.models.workout import Workout
    workout = Workout(
        name="Full Body Workout",
        description="A complete full body workout",
        difficulty="intermediate",
        duration=45,
        user_id=1
    )
    workout_history = WorkoutHistory(
        workout_id=1,
        user_id=1,
        duration=45
    )
    workout_history.workout = workout
    assert workout_history.workout.name == "Full Body Workout"
    assert workout_history.workout.difficulty == "intermediate"

def test_completed_exercise_validation():
    from app.models.workout_history import CompletedExercise
    with pytest.raises(ValueError):
        CompletedExercise(exercise_id=1, completed_sets=[])
    with pytest.raises(ValueError):
        CompletedExercise(
            exercise_id=1,
            completed_sets=[{"set_number": 1, "reps_completed": -1}]
        ) 