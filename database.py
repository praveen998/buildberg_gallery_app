from sqlalchemy import create_engine, Column, Integer, String,ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()
host = os.getenv("host")
port = int(os.getenv("port"))  # Convert to integer
user = os.getenv("user")
password = os.getenv("password")
db = os.getenv("db")
Base = declarative_base()


DATABASE_URL = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Gallery(Base):
    __tablename__="gallery"
    

Base.metadata.create_all(engine)

