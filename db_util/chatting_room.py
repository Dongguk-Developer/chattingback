from sqlalchemy import create_engine, Column, Integer, String, BigInteger, Enum, DateTime, ForeignKey, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import enum
from session import SessionLocal  # from session import SessionLocal에서 불러온 것을 사용함

Base = declarative_base()

# Enum for message types if needed
class ProfileImageTargetEnum(enum.Enum):
    chattingroom = "chattingroom"
    user = "user"

class ChattingRoom(Base):
    __tablename__ = 'chatting_room'

    room_id = Column(Integer, primary_key=True, autoincrement=True)
    # Define relationships
    hashtags = relationship("Hashtag", back_populates="chatting_room")
    messages = relationship("Message", back_populates="chatting_room")

class Hashtag(Base):
    __tablename__ = 'hashtag'

    hashtag_id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(Integer, ForeignKey('chatting_room.room_id'), nullable=False)
    tag = Column(String(255), nullable=False)

    # Relationship back to ChattingRoom
    chatting_room = relationship("ChattingRoom", back_populates="hashtags")

class Message(Base):
    __tablename__ = 'message'

    message_id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(Integer, ForeignKey('chatting_room.room_id'), nullable=False)
    sender_id = Column(BigInteger, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships with different message types
    images = relationship("MessageImage", back_populates="message")
    reads = relationship("MessageRead", back_populates="message")
    texts = relationship("MessageText", back_populates="message")
    videos = relationship("MessageVideo", back_populates="message")
    voices = relationship("MessageVoice", back_populates="message")

    # Relationship back to ChattingRoom
    chatting_room = relationship("ChattingRoom", back_populates="messages")

class MessageImage(Base):
    __tablename__ = 'message_image'

    image_id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(Integer, ForeignKey('message.message_id'), nullable=False)
    url = Column(String(255), nullable=False)

    # Relationship back to Message
    message = relationship("Message", back_populates="images")

class MessageRead(Base):
    __tablename__ = 'message_read'

    read_id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(Integer, ForeignKey('message.message_id'), nullable=False)
    user_id = Column(BigInteger, nullable=False)
    read_timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationship back to Message
    message = relationship("Message", back_populates="reads")

class MessageText(Base):
    __tablename__ = 'message_text'

    text_id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(Integer, ForeignKey('message.message_id'), nullable=False)
    content = Column(String(255), nullable=False)

    # Relationship back to Message
    message = relationship("Message", back_populates="texts")

class MessageVideo(Base):
    __tablename__ = 'message_video'

    video_id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(Integer, ForeignKey('message.message_id'), nullable=False)
    url = Column(String(255), nullable=False)

    # Relationship back to Message
    message = relationship("Message", back_populates="videos")

class MessageVoice(Base):
    __tablename__ = 'message_voice'

    voice_id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(Integer, ForeignKey('message.message_id'), nullable=False)
    url = Column(String(255), nullable=False)

    # Relationship back to Message
    message = relationship("Message", back_populates="voices")


# ChattingRoom CRUD
def create_chatting_room():
    with SessionLocal() as db:
        room = ChattingRoom()
        db.add(room)
        db.commit()
        db.refresh(room)
        return room

def get_chatting_room_by_id(room_id: int):
    with SessionLocal() as db:
        return db.query(ChattingRoom).filter(ChattingRoom.room_id == room_id).first()

def update_chatting_room(room_id: int):
    with SessionLocal() as db:
        room = db.query(ChattingRoom).filter(ChattingRoom.room_id == room_id).first()
        if room:
            db.commit()
            db.refresh(room)
        return room

def delete_chatting_room(room_id: int):
    with SessionLocal() as db:
        room = db.query(ChattingRoom).filter(ChattingRoom.room_id == room_id).first()
        if room:
            db.delete(room)
            db.commit()
            return True
        return False

# Hashtag CRUD
def create_hashtag(room_id: int, tag: str):
    with SessionLocal() as db:
        hashtag = Hashtag(room_id=room_id, tag=tag)
        db.add(hashtag)
        db.commit()
        db.refresh(hashtag)
        return hashtag

def get_hashtag_by_id(hashtag_id: int):
    with SessionLocal() as db:
        return db.query(Hashtag).filter(Hashtag.hashtag_id == hashtag_id).first()

def delete_hashtag(hashtag_id: int):
    with SessionLocal() as db:
        hashtag = db.query(Hashtag).filter(Hashtag.hashtag_id == hashtag_id).first()
        if hashtag:
            db.delete(hashtag)
            db.commit()
            return True
        return False

# Message CRUD
def create_message(room_id: int, sender_id: int):
    with SessionLocal() as db:
        message = Message(room_id=room_id, sender_id=sender_id, timestamp=datetime.utcnow())
        db.add(message)
        db.commit()
        db.refresh(message)
        return message

def get_message_by_id(message_id: int):
    with SessionLocal() as db:
        return db.query(Message).filter(Message.message_id == message_id).first()

def delete_message(message_id: int):
    with SessionLocal() as db:
        message = db.query(Message).filter(Message.message_id == message_id).first()
        if message:
            db.delete(message)
            db.commit()
            return True
        return False

# MessageImage CRUD
def create_message_image(message_id: int, url: str):
    with SessionLocal() as db:
        image = MessageImage(message_id=message_id, url=url)
        db.add(image)
        db.commit()
        db.refresh(image)
        return image

def get_message_image_by_id(image_id: int):
    with SessionLocal() as db:
        return db.query(MessageImage).filter(MessageImage.image_id == image_id).first()

def delete_message_image(image_id: int):
    with SessionLocal() as db:
        image = db.query(MessageImage).filter(MessageImage.image_id == image_id).first()
        if image:
            db.delete(image)
            db.commit()
            return True
        return False

# MessageRead CRUD
def create_message_read(message_id: int, user_id: int):
    with SessionLocal() as db:
        read = MessageRead(message_id=message_id, user_id=user_id, read_timestamp=datetime.utcnow())
        db.add(read)
        db.commit()
        db.refresh(read)
        return read

def get_message_read_by_id(read_id: int):
    with SessionLocal() as db:
        return db.query(MessageRead).filter(MessageRead.read_id == read_id).first()

def delete_message_read(read_id: int):
    with SessionLocal() as db:
        read = db.query(MessageRead).filter(MessageRead.read_id == read_id).first()
        if read:
            db.delete(read)
            db.commit()
            return True
        return False

# MessageText CRUD
def create_message_text(message_id: int, content: str):
    with SessionLocal() as db:
        text = MessageText(message_id=message_id, content=content)
        db.add(text)
        db.commit()
        db.refresh(text)
        return text

def get_message_text_by_id(text_id: int):
    with SessionLocal() as db:
        return db.query(MessageText).filter(MessageText.text_id == text_id).first()

def delete_message_text(text_id: int):
    with SessionLocal() as db:
        text = db.query(MessageText).filter(MessageText.text_id == text_id).first()
        if text:
            db.delete(text)
            db.commit()
            return True
        return False

# MessageVideo CRUD
def create_message_video(message_id: int, url: str):
    with SessionLocal() as db:
        video = MessageVideo(message_id=message_id, url=url)
        db.add(video)
        db.commit()
        db.refresh(video)
        return video

def get_message_video_by_id(video_id: int):
    with SessionLocal() as db:
        return db.query(MessageVideo).filter(MessageVideo.video_id == video_id).first()

def delete_message_video(video_id: int):
    with SessionLocal() as db:
        video = db.query(MessageVideo).filter(MessageVideo.video_id == video_id).first()
        if video:
            db.delete(video)
            db.commit()
            return True
        return False

# MessageVoice CRUD
def create_message_voice(message_id: int, url: str):
    with SessionLocal() as db:
        voice = MessageVoice(message_id=message_id, url=url)
        db.add(voice)
        db.commit()
        db.refresh(voice)
        return voice

def get_message_voice_by_id(voice_id: int):
    with SessionLocal() as db:
        return db.query(MessageVoice).filter(MessageVoice.voice_id == voice_id).first()

def delete_message_voice(voice_id: int):
    with SessionLocal() as db:
        voice = db.query(MessageVoice).filter(MessageVoice.voice_id == voice_id).first()
        if voice:
            db.delete(voice)
            db.commit()
            return True
        return False
