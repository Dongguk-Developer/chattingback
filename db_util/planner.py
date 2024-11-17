from sqlalchemy.ext.declarative import declarative_base
from db_util.db_session import SessionLocal
from datetime import date
from .models import Planner
Base = declarative_base()

def create_planner(planner_id:int,user_id: int, planner_date: date, planner_schedule_name: str, planner_schedule_status: str = None):
    with SessionLocal() as session:
        new_planner = Planner(
            planner_id=planner_id,
            user_id=user_id,
            planner_date=planner_date,
            planner_schedule_name=planner_schedule_name,
            planner_schedule_status=planner_schedule_status
        )

        session.add(new_planner)
        session.commit()
        session.refresh(new_planner)
        return new_planner
def get_planner_by_date(year: int, month: int, day: int):
    with SessionLocal() as session:
        target_date = date(year, month, day)
        return session.query(Planner).filter(Planner.planner_date == target_date).all()
def get_planner_by_id(planner_id: int):
    with SessionLocal() as session:
        return session.query(Planner).filter(Planner.planner_id == planner_id).first()

def get_planners_by_user_id(user_id: int):
    with SessionLocal() as session:
        return session.query(Planner).filter(Planner.user_id == user_id).all()

def update_planner(planner_id: int, planner_date: date = None, planner_schedule_name: str = None, planner_schedule_status: str = None):
    with SessionLocal() as session:
        planner = session.query(Planner).filter(Planner.planner_id == planner_id).first()
        if planner:
            if planner_date:
                planner.planner_date = planner_date
            if planner_schedule_name:
                planner.planner_schedule_name = planner_schedule_name
            if planner_schedule_status is not None:
                planner.planner_schedule_status = planner_schedule_status
            session.commit()
            session.refresh(planner)
        return planner

def delete_planner(planner_id: int):
    with SessionLocal() as session:
        planner = session.query(Planner).filter(Planner.planner_id == planner_id).first()
        if planner:
            session.delete(planner)
            session.commit()
        return planner
