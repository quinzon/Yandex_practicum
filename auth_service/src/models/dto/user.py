import re

import phonenumbers

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, SecretStr, field_validator

from typing import List, Any

from auth_service.src.models.dto.common import BaseDto


class UserCreate(BaseModel):
    email: EmailStr
    password: SecretStr = Field(..., min_length=8, max_length=128)
    first_name: str | None = Field(None, max_length=50)
    last_name: str | None = Field(None, max_length=50)
    patronymic: str | None = Field(None, max_length=50)
    phone_number: str | None = Field(None, max_length=20)

    @field_validator('password')
    def validate_password(cls, password: SecretStr) -> SecretStr:
        """Check password for having letters, numbers and special characters."""
        str_pass = password.get_secret_value()
        if not re.search(r'[A-Za-z]', str_pass):
            raise ValueError('Password must contain at least one letter.')

        if not re.search(r'\d', str_pass):
            raise ValueError('Password must contain at least one number.')

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', str_pass):
            raise ValueError('Password must contain at least one special character.')

        if re.search(r'\s', str_pass):
            raise ValueError('Password cannot contain spaces.')

        return password

    @field_validator('phone_number')
    def validate_phone_number(cls, phone_number):
        if phone_number is None:
            return None

        try:
            parsed_number = phonenumbers.parse(phone_number, None)  # Определение региона по номеру
            if not phonenumbers.is_valid_number(parsed_number):
                raise ValueError('Invalid phone number.')
            return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.NumberParseException:
            raise ValueError('Invalid phone number format. Ensure correct country code in E164 format.')


class UserResponse(BaseDto):
    id: str
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None
    patronymic: str | None = None
    phone_number: str | None = None
    roles: List[str] | None

    @field_validator('roles', mode='before')
    def convert_roles_to_strings(cls, roles: Any) -> List[str]:
        if roles is None:
            return []
        return [role.name if hasattr(role, 'name') else str(role) for role in roles]


class LoginRequest(BaseDto):
    email: EmailStr
    password: str


class UpdateProfileRequest(BaseModel):
    email: EmailStr | None = Field(None, description='Updated email address')
    first_name: str | None = Field(None, max_length=50, description='Updated first name')
    last_name: str | None = Field(None, max_length=50, description='Updated last name')
    patronymic: str | None = Field(None, max_length=50, description='Updated patronymic')
    phone_number: str | None = Field(None, max_length=20, description='Updated phone number')
    password: SecretStr | None = Field(None, min_length=8, description='New password')

    @field_validator('phone_number')
    def validate_phone_number(cls, phone_number: str | None) -> str | None:
        if phone_number is None:
            return None

        try:
            parsed_number = phonenumbers.parse(phone_number, None)
            if not phonenumbers.is_valid_number(parsed_number):
                raise ValueError('Invalid phone number.')
            return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.NumberParseException:
            raise ValueError('Invalid phone number format.')


class LoginHistoryResponse(BaseDto):
    id: str
    user_id: str
    user_agent: str
    ip_address: str
    timestamp: datetime
