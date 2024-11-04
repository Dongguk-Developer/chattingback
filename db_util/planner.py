from sqlalchemy import Column, Integer, BigInteger, Date, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine, Column, Integer, String,BigInteger,Enum,DateTime,ForeignKey, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
import enum
from urllib.parse import quote_plus
from datetime import datetime
from db_util.db_session import SessionLocal
from db_util.user_table import User

Base = declarative_base()
class Planner(Base):
    __tablename__ = 'planner'

    planner_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey(User.user_id), nullable=False)
    planner_date = Column(Date, nullable=False)
    planner_schedule_name = Column(String(60), nullable=False)  # charset, collation 제거
    planner_schedule_status = Column(String(45), nullable=True)  # charset, collation 제거

    # 관계 설정 (필요한 경우)
    # user = relationship("User", back_populates="planners")
from sqlalchemy.orm import Session
from datetime import date
# from .models import Planner  # Planner 클래스가 정의된 위치
from db_util.db_session import SessionLocal

# CRUD 함수 정의

# Create
def create_planner(planner_id:int,user_id: int, planner_date: date, planner_schedule_name: str, planner_schedule_status: str = None):
    with SessionLocal() as db:
        new_planner = Planner(
            planner_id=planner_id,
            user_id=user_id,
            planner_date=planner_date,
            planner_schedule_name=planner_schedule_name,
            planner_schedule_status=planner_schedule_status
        )
        db.add(new_planner)
        db.commit()
        db.refresh(new_planner)
        return new_planner

# Read by planner_id
def get_planner_by_id(planner_id: int):
    with SessionLocal() as db:
        return db.query(Planner).filter(Planner.planner_id == planner_id).first()

# Read by user_id
def get_planners_by_user_id(user_id: int):
    with SessionLocal() as db:
        return db.query(Planner).filter(Planner.user_id == user_id).all()

# Update
def update_planner(planner_id: int, planner_date: date = None, planner_schedule_name: str = None, planner_schedule_status: str = None):
    with SessionLocal() as db:
        planner = db.query(Planner).filter(Planner.planner_id == planner_id).first()
        if planner:
            if planner_date:
                planner.planner_date = planner_date
            if planner_schedule_name:
                planner.planner_schedule_name = planner_schedule_name
            if planner_schedule_status is not None:
                planner.planner_schedule_status = planner_schedule_status
            db.commit()
            db.refresh(planner)
        return planner

# Delete
def delete_planner(planner_id: int):
    with SessionLocal() as db:
        planner = db.query(Planner).filter(Planner.planner_id == planner_id).first()
        if planner:
            db.delete(planner)
            db.commit()
        return planner
