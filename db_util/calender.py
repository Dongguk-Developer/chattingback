from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError
from db_util.db_session import SessionLocal
from datetime import date,datetime
from .models import Calendar

Base = declarative_base()

def create_calendar(user_id: int,calender_id:int, start_date: date, finish_date: date, name: str, memo: str = None, isdday:bool=False):
    with SessionLocal() as session:
        new_calendar = Calendar(
            user_id=user_id,
            calender_id=calender_id,
            calender_date_start=start_date,
            calender_date_finish=finish_date,
            calender_schedule_name=name,
            calender_schedule_memo=memo,
            calender_is_dday=isdday
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

async def get_calendar_by_id(calender_id: int):
    with SessionLocal() as session:
        return session.query(Calendar).filter(Calendar.calender_id == calender_id).first()

def get_all_calendars():
    with SessionLocal() as session:
        return session.query(Calendar).all()
def get_all_calendars_by_user_id(user_id:int):
    with SessionLocal() as session:
        return session.query(Calendar).filter(Calendar.user_id==user_id).all()
def update_calendar(calender_id:int, start_date: date, finish_date: date, name: str, memo: str = None, isdday:bool=False):
    with SessionLocal() as session:
        try:
            calendar = session.query(Calendar).filter(Calendar.calender_id == calender_id).first()
            if calendar:
                if start_date is not None:
                    calendar.calender_date_start = start_date
                if finish_date is not None:
                    calendar.calender_date_finish = finish_date
                if name is not None:
                    calendar.calender_schedule_name = name
                if memo is not None:
                    calendar.calender_schedule_memo = memo
                if isdday is not None:
                    calendar.calender_is_dday = isdday


                session.commit()
                print(f"calendar updated: {calendar}")
                return calendar
            else:
                print("calendar not found.")
        except IntegrityError as e:
            session.rollback()
            print("IntegrityError occurred:", e)
        except Exception as e:
            session.rollback()
            print("Error occurred:", e)


def delete_calendar(calender_id: int):
    with SessionLocal() as session:
        calendar = session.query(Calendar).filter(Calendar.calender_id == calender_id).first()
        if not calendar:
            return None
        session.delete(calendar)
        session.commit()
        return calendar
def get_calender_in_date(start_date: str, end_date: str):
    try:
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
        with SessionLocal() as session:
            result = (
                session.query(Calendar)
                .filter(Calendar.calender_date_start >= start_datetime, Calendar.calender_date_finish < end_datetime)
                .all()
            )
            return result
    except Exception as e:
        return f"Error occurred: {str(e)}"