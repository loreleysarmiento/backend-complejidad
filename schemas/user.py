from datetime import datetime
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int
    registered_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    username: str | None = Field(None, max_length=50)
    password: str | None = Field(None, min_length=3, max_length=72)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: str | None = None
