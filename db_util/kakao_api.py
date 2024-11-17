# from . import connect
from sqlalchemy import create_engine, Column, Integer, String,BigInteger,Enum,DateTime,ForeignKey, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
import enum
from urllib.parse import quote_plus
from datetime import datetime
from db_util.db_session import SessionLocal
from .models import KakaoAPI
Base = declarative_base()




def create_kakao_api(k_id,
            kakao_id,
            kakao_name,
            kakao_tell,
            kakao_email,
            kakao_birth,
            kakao_create,
            kakao_update,
            kakao_image,
            kakao_refresh_token,
            kakao_access_token):
    with SessionLocal() as session:
        db_kakao = KakaoAPI(
            k_id=k_id,
            kakao_id=kakao_id,
            kakao_name=kakao_name,
            kakao_tell=kakao_tell,
            kakao_email=kakao_email,
            kakao_birth=kakao_birth,
            kakao_create=kakao_create,
            kakao_update=kakao_update,
            kakao_image=kakao_image,
            kakao_refresh_token=kakao_refresh_token,
            kakao_access_token=kakao_access_token
        )
        session.add(db_kakao)
        try:
            session.commit()
            session.refresh(db_kakao)
            return db_kakao
        except IntegrityError:
            session.rollback()
            raise

def get_kakao_api_by_id(k_id: int):
    with SessionLocal() as session:
        return session.query(KakaoAPI).filter(KakaoAPI.k_id == k_id).first()

def get_kakao_api_by_user_id(user_id: int):
    with SessionLocal() as session:
        return session.query(KakaoAPI).filter(KakaoAPI.kakao_id == user_id).first()

def update_kakao_api(k_id: int, updated_data):
    with SessionLocal() as session:
        db_kakao = session.query(KakaoAPI).filter(KakaoAPI.k_id == k_id).first()
        if db_kakao:
            db_kakao.kakao_name = updated_data.get("kakao_name", db_kakao.kakao_name)
            db_kakao.kakao_tell = updated_data.get("kakao_tell", db_kakao.kakao_tell)
            db_kakao.kakao_email = updated_data.get("kakao_email", db_kakao.kakao_email)
            db_kakao.kakao_birth = updated_data.get("kakao_birth", db_kakao.kakao_birth)
            db_kakao.kakao_update = datetime.utcnow()
            db_kakao.kakao_image = updated_data.get("kakao_image", db_kakao.kakao_image)
            db_kakao.kakao_refresh_token = updated_data.get("kakao_refresh_token", db_kakao.kakao_refresh_token)
            db_kakao.kakao_access_token = updated_data.get("kakao_access_token", db_kakao.kakao_access_token)
            
            session.commit()
            session.refresh(db_kakao)
            return db_kakao
        else:
            return None

# Delete a KakaoAPI record
def delete_kakao_api(k_id: int):
    with SessionLocal() as session:
        db_kakao = session.query(KakaoAPI).filter(KakaoAPI.k_id == k_id).first()
        if db_kakao:
            session.delete(db_kakao)
            session.commit()
            return True
        return False

# Usage example:
# Example data for creating a new record
# kakao_data = {
#     "kakao_id": 123456,
#     "kakao_name": "John Doe",
#     "kakao_tell": "010-1234-5678",
#     "kakao_email": "johndoe@example.com",
#     "kakao_birth": 1990,
#     "kakao_refresh_token": "refresh_token_example",
#     "kakao_access_token": "access_token_example"
# }

# new_kakao = create_kakao_api(kakao_data)
# retrieved_kakao = get_kakao_api_by_id(new_kakao.k_id)
# updated_kakao = update_kakao_api(new_kakao.k_id, {"kakao_name": "Jane Doe"})
# delete_kakao_api(new_kakao.k_id)
