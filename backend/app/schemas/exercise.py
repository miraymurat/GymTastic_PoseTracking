from pydantic import BaseModel
from typing import Optional

class ExerciseBase(BaseModel):
    name: str
    description: Optional[str] = None
    difficulty: Optional[str] = None
    muscle_group: Optional[str] = None
    equipment_needed: Optional[str] = None
    instructions: Optional[str] = None
    video_url: Optional[str] = None
    image_url: Optional[str] = None

class ExerciseCreate(ExerciseBase):
    pass

class ExerciseResponse(ExerciseBase):
    id: int

    class Config:
        orm_mode = True 