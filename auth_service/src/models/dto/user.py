import re
from pydantic import BaseModel, EmailStr, Field, SecretStr, field_validator
from typing import List
from uuid import UUID


class UserCreate(BaseModel):
    email: EmailStr
    password: SecretStr = Field(..., min_length=8, max_length=128)
    first_name: str | None = Field(None, max_length=50)
    last_name: str | None = Field(None, max_length=50)

    @field_validator('password')
    def validate_password(cls, password):
        """
        Сheck password for having letters, numbers and special characters
        """
        if not re.search(r"[A-Za-z]", password):
            raise ValueError("Password must contain at least one letter.")

        if not re.search(r"\d", password):
            raise ValueError("Password must contain at least one number.")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise ValueError("Password must contain at least one special character.")

        if re.search(r"\s", password):
            raise ValueError("Password cannot contain spaces.")

        return password


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    first_name: str | None
    last_name: str | None
    roles: List[str]

    class Config:
        orm_mode = True


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
