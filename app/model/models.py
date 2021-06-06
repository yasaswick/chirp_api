from fastapi.datastructures import UploadFile
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String , Float
from sqlalchemy.orm import relationship
from ..database.database import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    user_uuid = Column(UUID(as_uuid=True), unique=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    age = Column(Integer)
    bio = Column(String)
    joined_date = Column(String)
    profile_photo = Column(String)
    chat_messages = Column(Integer)
    token = Column(String)
    last_login = Column(String)
