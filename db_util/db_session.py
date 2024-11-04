# from . import connect
from sqlalchemy import create_engine, Column, Integer, String,BigInteger,Enum,DateTime,ForeignKey, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
import enum
from urllib.parse import quote_plus
import datetime
DB_USER = 'root'
DB_PASSWORD = 'rladlgus0625@'  # 비밀번호에 @가 포함된 경우
DB_HOST = 'localhost'
DB_NAME = 'studyhero-db'

# quote_plus()로 비밀번호를 URL 인코딩
encoded_password = quote_plus(DB_PASSWORD)

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{encoded_password}@{DB_HOST}/{DB_NAME}"
Base = declarative_base()
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

# Dependency to get a new session
def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()