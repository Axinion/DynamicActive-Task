from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    email: str
    name: str
    role: str


class LoginResponse(BaseModel):
    user: UserResponse
    access_token: Optional[str] = None
    token_type: str = "bearer"
