import sys
from sqlalchemy.orm import Session
import uuid

from sqlalchemy.sql.expression import null, func
from blog import models, schemas
from passlib.context import CryptContext

from core.db import data
from blog.schemas import Tag, UserInDB, TokenData
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# to get a string like this run: openssl rand -hex 32
SECRET_KEY = "3dd9c6b1fd99ec900cf7250041d24fedd637f1591a095616dee9d4befa71bd4e"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


"""Генрация токена"""
def gen_uuid():
    global uuid_var
    uuid_var = uuid.uuid4()
    return uuid_var

a = gen_uuid()
b = str(a)


"""Операции с паролем"""
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


"""Операции с User"""
def get_user_by_id(db:Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user(db: Session,username: str):
    z = db.query(models.User).filter(models.User.name == username).first()
    return z


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def authenticate_user(db:Session, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(name=username)
    except JWTError:
        raise credentials_exception
    user = get_user(data, username=token_data.name)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)):
    if current_user.is_active == False:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_user_by_name(db: Session, name: str):
    return db.query(models.User).filter(models.User.name == name).first()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(name=user.name, hashed_password=get_password_hash(user.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user




    """Операции с Post"""
def get_post_by_id(db: Session, post_id: int):
    return db.query(models.Post).filter(models.Post.id==post_id).all()


def get_tag_by_id(db: Session, tag_id: int):
    return db.query(models.Tag).filter(models.Tag.id==tag_id).one()


def get_post_by_time(db:Session, skip:str, limit:str):
    return db.query(models.Post).filter(models.Post.created_at >= skip, models.Post.created_at <= limit).all()


def get_post_id_by_tag_id(db: Session, tag_id: int):
    return db.query(models.Interaction).filter(models.Interaction.tag_id==tag_id).all()
    

def create_interaction(db:Session, post_id: int, tag_ids:int):
    db_inter = models.Interaction(post_id = post_id, tag_id = tag_ids)
    db.add(db_inter)
    db.commit()
    db.refresh(db_inter)
    return db_inter

def create_Post(db:Session, user_id:int, post:schemas.PostCreate):
    db_post = models.Post(owner_id = user_id, title=post.title, text=post.text)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


def delete_Post(db:Session, post_id: int, user_id: int):
    db_post = db.query(models.Post).filter(models.Post.id==post_id, models.Post.owner_id == user_id).one()
    db.delete(db_post)
    db.commit()
    db_tags = db.query(models.Interaction).filter(models.Interaction.post_id==post_id).all()
    db.delete(db_tags)
    db.commit()
    return True


def edit_Post(db:Session, post_id: int, post_title: str, post_text: str, user_id: int):
    db_post = db.query(models.Post).filter(models.Post.id==post_id, models.Post.owner_id == user_id).one()
    db_post.title = post_title
    db_post.text = post_text
    db.commit()
    db.refresh(db_post)
    return db_post


