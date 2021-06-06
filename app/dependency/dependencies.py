import json
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Security
from ..database.database import SessionLocal, engine
import pyrebase

from fastapi.security.api_key import APIKeyQuery, APIKeyCookie, APIKeyHeader, APIKey
from starlette.status import HTTP_403_FORBIDDEN


# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Firebase Storeage Dependency
# def get_stor():
#     pb = pyrebase.initialize_app(json.load(open('fbconfig.json')))


