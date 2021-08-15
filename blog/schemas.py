from core.db import Base
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime




"""pydantic Схемы Post и Tag"""

class PostBase(BaseModel):
    title: str


class PostCreate(PostBase):
    id: int
    text: str

    class Config:
            orm_mode = True 


class PostCreateReq(PostBase):
    id: int
    text: str
    tag_id: List=[]

    class Config:
            orm_mode = True 



class TagBase(BaseModel):
    id: int
    name: str


class PostforTag(PostBase):

    text: str
    created_at: datetime
    owner_id: int
    tags_id: List[TagBase]

    class Config:
            orm_mode = True



class TagCreate(TagBase):
    pass


class Tag(TagBase):
    posts2: List[PostforTag]


class PostforUser(PostBase):
    text: str

    class Config:
            orm_mode = True


"""pydantic Схема User"""
class UserBase(BaseModel):
    name: str


class UserCreate(UserBase):
    password: str


class UserInDB(UserBase):
    id: int
    is_active: bool
    hashed_password: str
    is_superuser: bool
    posts: List[PostforUser] = []

    class Config:
        orm_mode = True

class User(UserBase):
    id: int
    is_active: bool
    posts: List[PostforUser] = []
    created_at: datetime

    class Config:
        orm_mode = True



"""pydantic Схема Token"""
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    name: Optional[str] = None