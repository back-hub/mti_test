from operator import pos
from fastapi import APIRouter
from datetime import datetime, timedelta
from typing import List
from blog.crud import (
                        create_access_token,
                        get_current_active_user,
                        ACCESS_TOKEN_EXPIRE_MINUTES,
                        authenticate_user,
                        get_tag_by_id
)
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from blog import models, schemas, crud
from core.db import SessionLocal,engine,data
from blog.schemas import Token, UserInDB
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()




"""Установка зависимости открытия и закрытия сессии"""
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


"""Запросы для User"""
@router.post("/users/", response_model=schemas.User, tags=["Users"])
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_name(db, name=user.name)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Name already registered")
    return crud.create_user(db=db, user=user)

@router.get("/users/", response_model=List[schemas.User], tags=["Users"])
async def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/users/{user_id}", response_model=schemas.User, tags=["Users"])
async def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_id(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user


@router.get("/users/me/", response_model=schemas.User, tags=["Users"])
async def get_me(current_user: UserInDB = Depends(get_current_active_user)):
    return current_user



"""Log in"""
@router.post("/token", response_model=Token, tags=["Users"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.name}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}



"""Запросы для Post"""

@router.get("/users/posts/", tags=["Posts"])
async def get_posts(skip: str, limit: str, db: Session = Depends(get_db)):
    posts = crud.get_post_by_time(db, skip=skip, limit=limit)
    return posts



@router.get("/users/posts/{tag_id}", tags=["Posts"])
async def get_posts_by_tag_id(tag_id:int, db:Session=Depends(get_db)):
    post_ids = crud.get_post_id_by_tag_id(db=db, tag_id=tag_id)
    post_id_list = []
    for id in post_ids:
        post_id_list.append(id.post_id)
    result_list = []
    for id in post_id_list:
        result_list.append(crud.get_post_by_id(db=db,post_id=id)[0])
    
    return result_list
        



@router.post("/users/create/posts", response_model=schemas.PostCreate, tags=["Posts"])
async def create_post_by_user(
        post:schemas.PostCreateReq,
        current_user_state: UserInDB = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    for id in post.tag_id:
        try:
            db.query(models.Tag).filter(models.Tag.id==id).one()
        except:
            raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect tag id!"
        )
    user_id = current_user_state.id
    post_obj = crud.create_Post(db=db, user_id=user_id, post=post)
    for id in post.tag_id:
        crud.create_interaction(db=data, post_id=post_obj.id, tag_ids=id)
    return post_obj
    


@router.delete("/users/delete/posts/{post_id}", tags=["Posts"])
async def delete_post_by_user(
        post_id: int,
        current_user_state: UserInDB = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    user_id = current_user_state.id
    db_post = db.query(models.Post).filter(models.Post.id == post_id, models.Post.owner_id == user_id).first()
    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post doesn't exist!"
        )
    return crud.delete_Post(db=db, post_id=post_id, user_id=user_id)


@router.put("/users/posts", response_model=schemas.PostforUser, tags=["Posts"])
async def edit_post_by_user(
        post_id: int,
        post: schemas.PostforUser,
        current_user_state: UserInDB = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    user_id = current_user_state.id
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post doesn't exist!"
        )
    return crud.edit_Post(db=db, post_id=post_id, user_id=user_id, post_title=post.title, post_text=post.text)