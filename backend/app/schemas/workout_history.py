from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class WorkoutHistoryBase(BaseModel):
    exercise_name: str
    sets: int
    reps: Optional[int] = None
    duration: Optional[int] = None
    details: Optional[Dict[str, Any]] = None

class WorkoutHistoryCreate(WorkoutHistoryBase):
    pass

class WorkoutHistoryResponse(WorkoutHistoryBase):
    id: int
    user_id: int
    date: datetime

    class Config:
        orm_mode = True 