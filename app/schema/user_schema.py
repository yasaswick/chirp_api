# User Schemas
from typing import List
import uuid
from pydantic import BaseModel


class UserBase(BaseModel):
    email: str
    age: int
    bio:str
    profile_photo: str
    

class UserCreate(UserBase):
    password: str


class UserView(UserBase):
    id: int
    user_uuid:uuid.UUID
    joined_date:str
    chat_messages: int

    class Config:
        orm_mode = True


class UserViewPrivate(UserBase):
    id: int
    user_uuid:uuid.UUID
    joined_date:str
    chat_messages: int
    token: str

    class Config:
        orm_mode = True


class User(UserBase):
    id: int
    user_uuid:uuid.UUID
    joined_date:str
    chat_messages: int
    
    class Config:
        orm_mode = True

