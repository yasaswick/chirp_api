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
from fastapi.security.api_key import APIKeyQuery, APIKeyCookie, APIKeyHeader, APIKey

#router for this route
router = APIRouter(prefix="/user" , tags=["User"])

#storage instantiation
pb = pyrebase.initialize_app(json.load(open('fbconfig.json')))
storage = pb.storage()

#login route
@router.post("/login" ,  response_model=user_schema.UserViewPrivate)
def login_user(auth_details: AuthDetails, db: Session = Depends(get_db)):
    db_user = user_controller.get_user_by_email(db,email=auth_details.email)
    if (db_user is None) or (not user_controller.verify_password( plain_password = auth_details.password, hashed_password = db_user.hashed_password)):
        raise HTTPException(status_code=401, detail='Invalid username and/or password')
    token = user_controller.encode_token(db_user.email)
    db_user.token = token
    return db_user

#get user by token route
@router.get('/token',  response_model=user_schema.UserView)
def get_user_by_token(user_email = Depends(user_controller.auth_wrapper), db: Session = Depends(get_db)):
    db_user = user_controller.get_user_by_email(db, email= user_email)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

#check if email exists route
@router.get('/email')
def check_if_email_exists(user_email : str, db: Session = Depends(get_db)):
    db_user = user_controller.get_user_by_email(db, email= user_email)
    if db_user is None:
        return {'result': False}
    else:
        return {'result': True}

#create user route
@router.post("/", response_model=user_schema.UserViewPrivate)
def create_user(user_detail: user_schema.UserCreate, db: Session = Depends(get_db)):
    db_user = user_controller.get_user_by_email(db,email=user_detail.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = user_controller.get_password_hash(password= user_detail.password)
    user_detail.password = hashed_password
    new_user = user_controller.create_user(db=db, newuser=user_detail)
    token = user_controller.encode_token(new_user.email)
    new_user.token = token
    return new_user


#get all users route
@router.get("/", response_model=List[user_schema.UserView] )
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = user_controller.get_users(db, skip=skip, limit=limit)
    return users


#delete user route
@router.delete("/")
def delete_user_by_id(user_id:int , db: Session = Depends(get_db)):
     return user_controller.delete_user_by_id(db, user_id = user_id)

#upload profile image route
@router.post("/profile_image")
def upload_profile_image(user_email = Depends(user_controller.auth_wrapper), file: UploadFile = File(...) ,  db: Session = Depends(get_db)):
    db_user = user_controller.get_user_by_email(db, email= user_email)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    result = storage.child('user').child(str(db_user.user_uuid)).put(file.file)
    print(result)
    image_url = result['name']+'?alt=media&token='+result['downloadTokens']
    db_user.profile_photo = "https://firebasestorage.googleapis.com/v0/b/chirp-yasas.appspot.com/o/" + image_url.replace('/', '%2F')
    db.commit()
    return {"filename": image_url.replace('/', '%2F') }

#get user by uuid route
@router.get("/{user_uuid}", response_model=user_schema.UserView)
def read_user_by_uuid(user_uuid: str, db: Session = Depends(get_db)):
    db_user = user_controller.get_user_by_uuid(db, user_uuid=user_uuid)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

#get user by id route
@router.get("/id/{id}", response_model=user_schema.UserView)
def read_user_by_id(id: str, db: Session = Depends(get_db)):
    db_user = user_controller.get_user_by_id(db, id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


