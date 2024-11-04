from sqlalchemy import create_engine, Column, Integer, String,BigInteger,Enum,DateTime,Date,ForeignKey, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
import enum
from urllib.parse import quote_plus
from datetime import datetime
from session import SessionLocal
from datetime import date


Base = declarative_base()
class Calendar(Base):
    __tablename__ = 'calender'

    calender_id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(BigInteger, ForeignKey('users.user_id'), nullable=False)
    calender_date_start = Column(Date, nullable=False)
    calender_date_finish = Column(Date, nullable=False)
    calender_schedule_name = Column(String(60), nullable=False)
    calender_schedule_memo = Column(String(60), nullable=True)

    # Relationship with the `User` table if you have a User class
    user = relationship("User", back_populates="calendars")
def create_calendar(session, user_id: int, start_date: date, finish_date: date, name: str, memo: str = None):
    new_calendar = Calendar(
        user_id=user_id,
        calender_date_start=start_date,
        calender_date_finish=finish_date,
        calender_schedule_name=name,
        calender_schedule_memo=memo
    )
    session.add(new_calendar)
    try:
        session.commit()
        session.refresh(new_calendar)
        return new_calendar
    except IntegrityError:
        session.rollback()
        print("Error: Could not create calendar entry. Please check foreign key constraints.")
        return None

def get_calendar_by_id(session, calender_id: int):
    return session.query(Calendar).filter(Calendar.calender_id == calender_id).first()

def get_all_calendars(session):
    return session.query(Calendar).all()

def update_calendar(session, calender_id: int, **kwargs):
    calendar = get_calendar_by_id(session, calender_id)
    if not calendar:
        print("Calendar entry not found.")
        return None

    for key, value in kwargs.items():
        if hasattr(calendar, key):
            setattr(calendar, key, value)

    session.commit()
    session.refresh(calendar)
    return calendar

def delete_calendar(session, calender_id: int):
    calendar = get_calendar_by_id(session, calender_id)
    if not calendar:
        print("Calendar entry not found.")
        return None

    session.delete(calendar)
    session.commit()
    return calendar