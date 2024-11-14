from db_util.db_session import SessionLocal

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError
from .models import Hashtag
Base = declarative_base()



# Create (Insert) a new Hashtag record
def create_hashtag(room_id: int, tag: str):
    with SessionLocal() as session:
        hashtag = Hashtag(room_id=room_id, tag=tag)
        session.add(hashtag)
        try:
            session.commit()
            session.refresh(hashtag)
            return hashtag
        except IntegrityError:
            session.rollback()
            raise

# Read (Retrieve) a Hashtag record by ID
def get_hashtag_by_id(hashtag_id: int):
    with SessionLocal() as session:
        return session.query(Hashtag).filter(Hashtag.hashtag_id == hashtag_id).first()

# Update an existing Hashtag record
def update_hashtag(hashtag_id: int, new_tag: str):
    with SessionLocal() as session:
        hashtag = session.query(Hashtag).filter(Hashtag.hashtag_id == hashtag_id).first()
        if hashtag:
            hashtag.tag = new_tag
            session.commit()
            session.refresh(hashtag)
            return hashtag
        else:
            return None

# Delete a Hashtag record
def delete_hashtag(hashtag_id: int):
    with SessionLocal() as session:
        hashtag = session.query(Hashtag).filter(Hashtag.hashtag_id == hashtag_id).first()
        if hashtag:
            session.delete(hashtag)
            session.commit()
            return True
        return False