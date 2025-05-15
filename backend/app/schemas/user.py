from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    profile_picture: Optional[str] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    profile_picture: Optional[str] = None
    last_login: Optional[datetime] = None
    has_profile: bool = False

    class Config:
        orm_mode = True

class GoogleAuthData(BaseModel):
    idToken: str
    email: str
    name: Optional[str] = None
    photo: Optional[str] = None

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
    isNewUser: bool = False 