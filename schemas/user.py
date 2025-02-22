from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from datetime import datetime


class User(BaseModel):
    id: int
    username: str
    email: str
    verified: bool
    created_at: datetime  # Asegúrate que tu modelo de base de datos tenga este campo

    class Config:
        orm_mode = True

# Esquema base común
from pydantic import BaseModel, EmailStr, constr
from datetime import datetime


class UserBase(BaseModel):
    username: constr(min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    password: constr(min_length=8)


class UserResponse(UserBase):
    id: int
    verified: bool
    created_at: datetime

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class VerifyRequest(BaseModel):
    email: EmailStr
    code: int


class ResendCodeRequest(BaseModel):
    email: EmailStr


class UpdatePasswordRequest(BaseModel):
    current_password: str
    new_password: constr(min_length=8)