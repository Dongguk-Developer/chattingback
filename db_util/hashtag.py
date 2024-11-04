from session import SessionLocal
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError
Base = declarative_base()

class Hashtag(Base):
    __tablename__ = 'hashtag'

    hashtag_id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(Integer, ForeignKey('chatting_room.room_id'), nullable=False)
    tag = Column(String(255), nullable=False)

    # Relationship back to ChattingRoom
    chatting_room = relationship("ChattingRoom", back_populates="hashtags")

    def __repr__(self):
        return f"<Hashtag(hashtag_id={self.hashtag_id}, room_id={self.room_id}, tag='{self.tag}')>"



# Create (Insert) a new Hashtag record
def create_hashtag(room_id: int, tag: str):
    with SessionLocal() as db:
        hashtag = Hashtag(room_id=room_id, tag=tag)
        db.add(hashtag)
        try:
            db.commit()
            db.refresh(hashtag)
            return hashtag
        except IntegrityError:
            db.rollback()
            raise

# Read (Retrieve) a Hashtag record by ID
def get_hashtag_by_id(hashtag_id: int):
    with SessionLocal() as db:
        return db.query(Hashtag).filter(Hashtag.hashtag_id == hashtag_id).first()

# Update an existing Hashtag record
def update_hashtag(hashtag_id: int, new_tag: str):
    with SessionLocal() as db:
        hashtag = db.query(Hashtag).filter(Hashtag.hashtag_id == hashtag_id).first()
        if hashtag:
            hashtag.tag = new_tag
            db.commit()
            db.refresh(hashtag)
            return hashtag
        else:
            return None

# Delete a Hashtag record
def delete_hashtag(hashtag_id: int):
    with SessionLocal() as db:
        hashtag = db.query(Hashtag).filter(Hashtag.hashtag_id == hashtag_id).first()
        if hashtag:
            db.delete(hashtag)
            db.commit()
            return True
        return False