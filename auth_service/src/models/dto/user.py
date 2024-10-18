import re
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, SecretStr, field_validator
from typing import List, Optional

from auth_service.src.models.dto.common import BaseDto


class UserCreate(BaseModel):
    email: EmailStr
    password: SecretStr = Field(..., min_length=8, max_length=128)
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)

    @field_validator('password')
    def validate_password(cls, password: SecretStr) -> SecretStr:
        """
        Сheck password for having letters, numbers and special characters
        """
        str_pass = password.get_secret_value()
        if not re.search(r'[A-Za-z]', str_pass):
            raise ValueError('Password must contain at least one letter.')

        if not re.search(r'\d', str_pass):
            raise ValueError('Password must contain at least one number.')

        if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', str_pass):
            raise ValueError('Password must contain at least one special character.')

        if re.search(r'\s', str_pass):
            raise ValueError('Password cannot contain spaces.')

        return password


class UserResponse(BaseDto):
    id: str
    email: EmailStr
    first_name: Optional[str]
    last_name: Optional[str]
    roles: Optional[List[str]] = None

    @field_validator('id', mode='before')
    def convert_uuid_to_str(cls, value):
        if isinstance(value, UUID):
            return str(value)
        return value


class LoginRequest(BaseDto):
    email: EmailStr
    password: str


class UpdateProfileRequest(BaseModel):
    email: EmailStr | None = Field(None, description='Updated email address')
    first_name: str | None = Field(None, max_length=50, description='Updated first name')
    last_name: str | None = Field(None, max_length=50, description='Updated last name')
    password: SecretStr | None = Field(None, min_length=8, description='New password')
