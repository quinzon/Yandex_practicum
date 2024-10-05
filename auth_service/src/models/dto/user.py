from pydantic import BaseModel, EmailStr, Field
from uuid import UUID


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    first_name: str | None = Field(None, max_length=50)
    last_name: str | None = Field(None, max_length=50)

class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    first_name: str | None
    last_name: str | None

    class Config:
        orm_mode = True
