from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# this is the database url for the postgresql database
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

# this will create the bind between databse and api 
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# this will create a database sessions 
SessionLocal = sessionmaker(
                autocommit=False, 
                autoflush=False, 
                bind=engine
                )

# i dont know about this line. Learn about it ;)
Base = declarative_base()

# function used for creating a instance of 
# database sessions and closing it when operations complete
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()