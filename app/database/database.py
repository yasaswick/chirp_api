from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


SQLALCHEMY_DATABASE_URL = "postgres://onifbpgaaewbeu:ad3eb211b6cd1b8824f16eb8baadc74576236e3a94d92c5b3e8896a2a9b1af67@ec2-35-169-188-58.compute-1.amazonaws.com:5432/dfsdgsaj7606vj"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()