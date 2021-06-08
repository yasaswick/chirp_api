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


#Authentication Wrappers 
security = HTTPBearer()
#For token generation
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
secret = 'SECRET'

#method to get user by id
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

#method to get user by uuid
def get_user_by_uuid(db: Session, user_uuid: str):
    return db.query(models.User).filter(models.User.user_uuid == user_uuid).first()

#method to get user by id
def get_user_by_id(db: Session, id: str):
    return db.query(models.User).filter(models.User.id == id).first()

#method to keep count of chat messages (removed this temporarily)
async def user_sent_message_count(db: Session, id: str):
    dbUser = await db.query(models.User).filter(models.User.id == id).first()
    dbUser.chat_messages += 1
    await db.add(dbUser)
    print(dbUser)
    await db.commit()
    return {'success'}

#method to get user by emai
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

#mehod to get all users
def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

#method to delete user by id
def delete_user_by_id(db: Session, user_id :int):
    dbuser = db.query(models.User).get(user_id)
    db.delete(dbuser)
    db.commit()
    return {'message': 'User successfully deleted'}

#method to create user
def create_user(db: Session, newuser: user_schema.UserCreate):
    db_user = models.User(
    name = newuser.name,    
    email= newuser.email, 
    age = newuser.age,
    bio = newuser.bio,
    hashed_password = newuser.password,
    joined_date = time.time(),
    profile_photo = newuser.profile_photo,
    chat_messages = 0
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

#method to encode token
def encode_token( user_id):
    payload = {
        'exp': datetime.utcnow() + timedelta(days=15, minutes=5),
        'iat': datetime.utcnow(),
        'sub': user_id
        }
    return jwt.encode(payload,secret,algorithm='HS256')

#method to decode token
def decode_token( token):
    try:
        payload = jwt.decode(token, secret, algorithms=['HS256'])
        return payload['sub']
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Signature has expired')
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail='Invalid token')

#auth wrappers
def auth_wrapper( auth: HTTPAuthorizationCredentials = Security(security)):
    return decode_token(auth.credentials)
    
#password encryption 
def get_password_hash(password):
    return pwd_context.hash(password)

#password verification 
def verify_password( plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)