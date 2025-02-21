from typing import Optional
from pydantic import BaseModel, EmailStr

class User(BaseModel):
    id: Optional[int] = None
    username: str
    email: EmailStr
    password: str
    verification_code: Optional[int] = None  # Campo opcional
    verified: bool = False  # Campo con valor por defecto

class UserCount(BaseModel):
    total: int

class UserLogin(BaseModel):
    email: str
    password: str