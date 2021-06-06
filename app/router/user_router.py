import os
from fastapi.datastructures import UploadFile
from fastapi.params import File
from requests.sessions import session
from app.model.auth_details import AuthDetails
from typing import List
from fastapi import APIRouter
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql.sqltypes import String
from ..dependency.dependencies import  get_db
from ..schema import user_schema
from ..controller import user_controller
import json
import pyrebase
import tempfile
from firebase_admin import credentials, auth ,storage
from fastapi.security.api_key import APIKeyQuery, APIKeyCookie, APIKeyHeader, APIKey

router = APIRouter(prefix="/user" , tags=["User"])


@router.post("/login")
def login_user(auth_details: AuthDetails, db: Session = Depends(get_db)):
    db_user = user_controller.get_user_by_email(db,email=auth_details.email)
    if (db_user is None) or (not user_controller.verify_password( plain_password = auth_details.password, hashed_password = db_user.hashed_password)):
        raise HTTPException(status_code=401, detail='Invalid username and/or password')
    token = user_controller.encode_token(db_user.email)
    return { 'token': token }

@router.get('/token',  response_model=user_schema.UserView)
def get_user_by_token(user_email = Depends(user_controller.auth_wrapper), db: Session = Depends(get_db)):
    db_user = user_controller.get_user_by_email(db, email= user_email)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.get('/email')
def check_if_email_exists(user_email : str, db: Session = Depends(get_db)):
    db_user = user_controller.get_user_by_email(db, email= user_email)
    if db_user is None:
        return {'result': False}
    else:
        return {'result': True}


@router.post("/", response_model=user_schema.UserView)
def create_user(user_detail: user_schema.UserCreate, db: Session = Depends(get_db)):
    db_user = user_controller.get_user_by_email(db,email=user_detail.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = user_controller.get_password_hash(password= user_detail.password)
    user_detail.password = hashed_password
    return user_controller.create_user(db=db, newuser=user_detail)


@router.get("/", response_model=List[user_schema.UserView] )
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = user_controller.get_users(db, skip=skip, limit=limit)
    return users

    
@router.delete("/")
def delete_user_by_id(user_id:int , db: Session = Depends(get_db)):
     return user_controller.delete_user_by_id(db, user_id = user_id)

@router.post("/profile_image")
def upload_profile_image(user_email = Depends(user_controller.auth_wrapper), file: UploadFile = File(...) ,  db: Session = Depends(get_db)):
    db_user = user_controller.get_user_by_email(db, email= user_email)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    result = storage.child('user').child(str(db_user.user_uuid)).put(file.file)
    db_user.profile_photo = result['name']+'?alt=media&token='+result['downloadTokens']
    db.commit()
    return {"filename": result['name']+'?alt=media&token='+result['downloadTokens']}

    
@router.get("/{user_uuid}", response_model=user_schema.UserView)
def read_user_by_uuid(user_uuid: str, db: Session = Depends(get_db)):
    db_user = user_controller.get_user_by_uuid(db, user_uuid=user_uuid)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


