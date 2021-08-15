from sqlalchemy import Column, String, Integer, DateTime, sql
from sqlalchemy.sql.expression import table
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Boolean, TIMESTAMP
from core.db import Base, SessionLocal






class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, unique=True)
    name = Column(String, unique=True)
    hashed_password = Column(String)
    created_at = Column(TIMESTAMP, default=sql.func.now())
    is_active = Column(Boolean, default=False)
    is_admin = Column(Boolean,default=False)

    posts = relationship("Post", back_populates="owner")



class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True,unique=True)
    title = Column(String)
    text = Column(String(350))
    created_at = Column(TIMESTAMP, default=sql.func.now())
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    owner = relationship("User", back_populates="posts")



class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True, unique=True)
    name = Column(String)
    



class Interaction(Base):
    __tablename__ = "interaction"

    id = Column(Integer, primary_key=True, index=True,unique=True)
    post_id = Column(Integer)
    tag_id = Column(Integer)