import jwt
from operator import imod
from sqlalchemy.orm import Session
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from ..schema import user_schema
from ..model import models
from datetime import datetime, timedelta
import time



security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
secret = 'SECRET'

def get_user(db: Session, user_id: int):
    return db.query(models.user.User).filter(models.user.User.id == user_id).first()

def get_user_by_uuid(db: Session, user_uuid: str):
    return db.query(models.user.User).filter(models.user.User.user_uuid == user_uuid).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.user.User).filter(models.user.User.email == email).first()
    
def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.user.User).offset(skip).limit(limit).all()

def delete_user_by_id(db: Session, user_id :int):
    dbuser = db.query(models.user.User).get(user_id)
    db.delete(dbuser)
    db.commit()
    return {'message': 'User successfully deleted'}


def create_user(db: Session, newuser: user_schema.UserCreate):
    db_user = models.user.User(email= newuser.email, 
    user_id = newuser.user_id,
    dob = newuser.dob,
    phone = newuser.phone,
    bio = newuser.bio,
    hashed_password = newuser.password,
    joined_date = time.time(),
    location = newuser.location,
    profile_photo = newuser.profile_photo,
    banner_photo = newuser.banner_photo
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def encode_token( user_id):
    payload = {
        'exp': datetime.utcnow() + timedelta(days=1, minutes=5),
        'iat': datetime.utcnow(),
        'sub': user_id
        }
    return jwt.encode(payload,secret,algorithm='HS256')


def decode_token( token):
    try:
        payload = jwt.decode(token, secret, algorithms=['HS256'])
        return payload['sub']
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Signature has expired')
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail='Invalid token')


def auth_wrapper( auth: HTTPAuthorizationCredentials = Security(security)):
    return decode_token(auth.credentials)
    

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password( plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)