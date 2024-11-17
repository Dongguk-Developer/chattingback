# from . import connect
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus
import os
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']  # 비밀번호에 @가 포함된 경우
DB_HOST = os.environ['DB_HOST']
DB_NAME = os.environ['DB_NAME']

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