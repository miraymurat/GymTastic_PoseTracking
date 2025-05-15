from pydantic import BaseModel
from typing import Optional, List
from app.schemas.exercise import ExerciseResponse

class WorkoutBase(BaseModel):
    name: str
    description: Optional[str] = None
    duration: Optional[int] = None
    difficulty: Optional[str] = None

class WorkoutCreate(WorkoutBase):
    exercise_ids: List[int] = []

class WorkoutUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[int] = None
    difficulty: Optional[str] = None
    exercise_ids: Optional[List[int]] = None

class WorkoutResponse(WorkoutBase):
    id: int
    created_by: int
    exercises: List[ExerciseResponse] = []

    class Config:
        orm_mode = True 