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

Base = declarative_base()


class KakaoAPI(Base):
    __tablename__ = 'kakao_api'
    
    k_id = Column(BigInteger, primary_key=True, autoincrement=True)
    kakao_id = Column(BigInteger, nullable=False)
    kakao_name = Column(String(45, collation='utf8mb4_general_ci'), nullable=False)
    kakao_tell = Column(String(45, collation='utf8mb4_general_ci'), nullable=False)
    kakao_email = Column(String(45, collation='utf8mb4_general_ci'), nullable=False)
    kakao_birth = Column(Integer, nullable=False)
    kakao_create = Column(DateTime, default=None)
    kakao_update = Column(DateTime, default=None)
    kakao_image = Column(String(255, collation='utf8mb4_general_ci'), default=None)
    kakao_refresh_token = Column(String(255, collation='utf8mb4_general_ci'), nullable=False)
    kakao_access_token = Column(String(255, collation='utf8mb4_general_ci'), nullable=False)

    def __repr__(self):
        return (f"<KakaoAPI(k_id={self.k_id}, kakao_id={self.kakao_id}, kakao_name='{self.kakao_name}', "
                f"kakao_tell='{self.kakao_tell}', kakao_email='{self.kakao_email}', kakao_birth={self.kakao_birth}, "
                f"kakao_create={self.kakao_create}, kakao_update={self.kakao_update}, kakao_image='{self.kakao_image}', "
                f"kakao_refresh_token='{self.kakao_refresh_token}', kakao_access_token='{self.kakao_access_token}')>")



# Create (Insert) a new KakaoAPI record
def create_kakao_api(kakao_data):
    with SessionLocal() as db:
        db_kakao = KakaoAPI(
            kakao_id=kakao_data["kakao_id"],
            kakao_name=kakao_data["kakao_name"],
            kakao_tell=kakao_data["kakao_tell"],
            kakao_email=kakao_data["kakao_email"],
            kakao_birth=kakao_data["kakao_birth"],
            kakao_create=datetime.utcnow(),
            kakao_update=datetime.utcnow(),
            kakao_image=kakao_data.get("kakao_image"),
            kakao_refresh_token=kakao_data["kakao_refresh_token"],
            kakao_access_token=kakao_data["kakao_access_token"]
        )
        db.add(db_kakao)
        try:
            db.commit()
            db.refresh(db_kakao)
            return db_kakao
        except IntegrityError:
            db.rollback()
            raise

# Read (Retrieve) a KakaoAPI record by ID
def get_kakao_api_by_id(k_id: int):
    with SessionLocal() as db:
        return db.query(KakaoAPI).filter(KakaoAPI.k_id == k_id).first()

# Update an existing KakaoAPI record
def update_kakao_api(k_id: int, updated_data):
    with SessionLocal() as db:
        db_kakao = db.query(KakaoAPI).filter(KakaoAPI.k_id == k_id).first()
        if db_kakao:
            db_kakao.kakao_name = updated_data.get("kakao_name", db_kakao.kakao_name)
            db_kakao.kakao_tell = updated_data.get("kakao_tell", db_kakao.kakao_tell)
            db_kakao.kakao_email = updated_data.get("kakao_email", db_kakao.kakao_email)
            db_kakao.kakao_birth = updated_data.get("kakao_birth", db_kakao.kakao_birth)
            db_kakao.kakao_update = datetime.utcnow()
            db_kakao.kakao_image = updated_data.get("kakao_image", db_kakao.kakao_image)
            db_kakao.kakao_refresh_token = updated_data.get("kakao_refresh_token", db_kakao.kakao_refresh_token)
            db_kakao.kakao_access_token = updated_data.get("kakao_access_token", db_kakao.kakao_access_token)
            
            db.commit()
            db.refresh(db_kakao)
            return db_kakao
        else:
            return None

# Delete a KakaoAPI record
def delete_kakao_api(k_id: int):
    with SessionLocal() as db:
        db_kakao = db.query(KakaoAPI).filter(KakaoAPI.k_id == k_id).first()
        if db_kakao:
            db.delete(db_kakao)
            db.commit()
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
