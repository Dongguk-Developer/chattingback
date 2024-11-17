from db_util.db_session import SessionLocal
from sqlalchemy.ext.declarative import declarative_base
from .models import Hashtag,ChattingRoom
Base = declarative_base()

def create_hashtag(hashtag_id:int,room_id: int, tag: str):
    try:
        with SessionLocal() as session:
            room_exists = session.query(ChattingRoom).filter_by(room_id=room_id).first()
            if not room_exists:
                raise ValueError(f"Room with id {room_id} does not exist in `chatting_room` table.")
            hashtag = Hashtag(hashtag_id=hashtag_id,room_id=room_id, hashtag_title=tag)
            session.add(hashtag)
            session.commit()
            session.refresh(hashtag)
            return hashtag
    except Exception as e:
        raise e

def get_hashtag_by_id(hashtag_id: int):
    with SessionLocal() as session:
        return session.query(Hashtag).filter(Hashtag.hashtag_id == hashtag_id).first()

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

def delete_hashtag(hashtag_id: int):
    with SessionLocal() as session:
        hashtag = session.query(Hashtag).filter(Hashtag.hashtag_id == hashtag_id).first()
        if hashtag:
            session.delete(hashtag)
            session.commit()
            return True
        return False