# from sqlalchemy import create_engine, Column, Integer, String, BigInteger, Enum, DateTime, ForeignKey, TIMESTAMP
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import relationship, sessionmaker
# from datetime import datetime
# import enum
from db_util.db_session import SessionLocal
# from sqlalchemy import func, desc
from db_util.user_table import User


from sqlalchemy import create_engine, Column, Integer, String, BigInteger, ForeignKey, TIMESTAMP, DateTime
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import func, desc
from db_util.room_users import RoomUser
from db_util.profile_image import ProfileImage
from .models import ChattingRoom,Message


# ChattingRoom CRUD
def create_chatting_room(room_id, profile_image_id, room_type, room_name, room_manager, room_total_users):
    with SessionLocal() as session:
        new_room = ChattingRoom(
            room_id=room_id,
            profile_image_id=profile_image_id,
            room_type=room_type,
            room_name=room_name,
            room_manager=room_manager,
            room_total_users=room_total_users,
            room_create=datetime.utcnow()
        )
        session.add(new_room)
        session.commit()
        session.refresh(new_room)
        return new_room

def get_chatting_room_by_id(room_id: int):
    with SessionLocal() as session:
        return session.query(ChattingRoom).filter(ChattingRoom.room_id == room_id).first()

def update_chatting_room(room_id: int, room_name: Optional[str] = None, room_total_users: Optional[int] = None):
    with SessionLocal() as session:
        room = session.query(ChattingRoom).filter(ChattingRoom.room_id == room_id).first()
        if room:
            if room_name:
                room.room_name = room_name
            if room_total_users is not None:
                room.room_total_users = room_total_users
            session.commit()
            session.refresh(room)
        return room

def delete_chatting_room(room_id: int):
    with SessionLocal() as session:
        room = session.query(ChattingRoom).filter(ChattingRoom.room_id == room_id).first()
        if room:
            session.delete(room)
            session.commit()
            return True
        return False

def create_message(room_id: int, sender_id: int):
    with SessionLocal() as session:
        message = Message(room_id=room_id, sender_id=sender_id, timestamp=datetime.utcnow())
        session.add(message)
        session.commit()
        session.refresh(message)
        return message

def get_message_by_id(message_id: int):
    with SessionLocal() as session:
        return session.query(Message).filter(Message.message_id == message_id).first()

def delete_message(message_id: int):
    with SessionLocal() as session:
        message = session.query(Message).filter(Message.message_id == message_id).first()
        if message:
            session.delete(message)
            session.commit()
            return True
        return False

# Example function for getting top chatrooms
def get_top_chatrooms():
    with SessionLocal() as session:
        result = (
            session.query(
                RoomUser.room_id,
                func.sum(User.user_xp).label('total_xp')
            )
            .join(User, User.user_id == RoomUser.user_id)
            .group_by(RoomUser.room_id)
            .order_by(desc('total_xp'))
            .limit(5)
            .all()
        )
        return result
# from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, TIMESTAMP
# from sqlalchemy.orm import relationship, Session
# from datetime import datetime
# from typing import Optional, List
# from sqlalchemy.ext.declarative import declarative_base
# from db_util.user_table import ProfileImage

# Base = declarative_base()

# class ChattingRoom(Base):
#     __tablename__ = 'chatting_rooms'

#     room_id = Column(Integer, primary_key=True)
#     profile_image_id = Column(Integer, ForeignKey('profile_image.profile_image_id'), nullable=False)
#     room_type = Column(String(45), nullable=False)
#     room_name = Column(String(45), nullable=False)
#     room_manager = Column(BigInteger, nullable=False)
#     room_create = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
#     room_total_users = Column(Integer, nullable=False)

#     # Relationship to Message
#     # messages = relationship("Message", back_populates="chatting_room")

# class Message(Base):
#     __tablename__ = 'message'

#     message_id = Column(Integer, primary_key=True, autoincrement=True)
#     room_id = Column(Integer, ForeignKey('chatting_rooms.room_id'), nullable=False)
#     sender_id = Column(BigInteger, nullable=False)
#     timestamp = Column(DateTime, default=datetime.utcnow)

#     # Relationships with different message types
#     # images = relationship("MessageImage", back_populates="message")
#     # reads = relationship("MessageRead", back_populates="message")
#     # texts = relationship("MessageText", back_populates="message")
#     # videos = relationship("MessageVideo", back_populates="message")
#     # voices = relationship("MessageVoice", back_populates="message")

#     # # Relationship back to ChattingRoom
#     # chatting_room = relationship("ChattingRoom", back_populates="messages")

# class MessageImage(Base):
#     __tablename__ = 'message_image'

#     image_id = Column(Integer, primary_key=True, autoincrement=True)
#     message_id = Column(Integer, ForeignKey('message.message_id'), nullable=False)
#     url = Column(String(255), nullable=False)

#     # Relationship back to Message
#     # message = relationship("Message", back_populates="images")

# class MessageRead(Base):
#     __tablename__ = 'message_read'

#     read_id = Column(Integer, primary_key=True, autoincrement=True)
#     message_id = Column(Integer, ForeignKey('message.message_id'), nullable=False)
#     user_id = Column(BigInteger, nullable=False)
#     read_timestamp = Column(DateTime, default=datetime.utcnow)

#     # Relationship back to Message
#     # message = relationship("Message", back_populates="reads")

# class MessageText(Base):
#     __tablename__ = 'message_text'

#     text_id = Column(Integer, primary_key=True, autoincrement=True)
#     message_id = Column(Integer, ForeignKey('message.message_id'), nullable=False)
#     content = Column(String(255), nullable=False)

#     # Relationship back to Message
#     # message = relationship("Message", back_populates="texts")

# class MessageVideo(Base):
#     __tablename__ = 'message_video'

#     video_id = Column(Integer, primary_key=True, autoincrement=True)
#     message_id = Column(Integer, ForeignKey('message.message_id'), nullable=False)
#     url = Column(String(255), nullable=False)

#     # Relationship back to Message
#     # message = relationship("Message", back_populates="videos")

# class MessageVoice(Base):
#     __tablename__ = 'message_voice'

#     voice_id = Column(Integer, primary_key=True, autoincrement=True)
#     message_id = Column(Integer, ForeignKey('message.message_id'), nullable=False)
#     url = Column(String(255), nullable=False)

#     # Relationship back to Message
#     # message = relationship("Message", back_populates="voices")

# # ChattingRoom CRUD
# def create_chatting_room(room_id, profile_image_id, room_type, room_name, room_manager, room_total_users):
#     with SessionLocal() as session:
#         new_room = ChattingRoom(
#             room_id=room_id,
#             profile_image_id=profile_image_id,
#             room_type=room_type,
#             room_name=room_name,
#             room_manager=room_manager,
#             room_total_users=room_total_users,
#             room_create=datetime.utcnow()
#         )
#         session.add(new_room)
#         session.commit()
#         session.refresh(new_room)
#         return new_room

# def get_chatting_room_by_id(room_id: int):
#     with SessionLocal() as session:
#         return session.query(ChattingRoom).filter(ChattingRoom.room_id == room_id).first()

# def update_chatting_room(room_id: int, room_name: Optional[str] = None, room_total_users: Optional[int] = None):
#     with SessionLocal() as session:
#         room = session.query(ChattingRoom).filter(ChattingRoom.room_id == room_id).first()
#         if room:
#             if room_name:
#                 room.room_name = room_name
#             if room_total_users is not None:
#                 room.room_total_users = room_total_users
#             session.commit()
#             session.refresh(room)
#         return room

# def delete_chatting_room(room_id: int):
#     with SessionLocal() as session:
#         room = session.query(ChattingRoom).filter(ChattingRoom.room_id == room_id).first()
#         if room:
#             session.delete(room)
#             session.commit()
#             return True
#         return False

# def create_message(room_id: int, sender_id: int):
#     with SessionLocal() as session:
#         message = Message(room_id=room_id, sender_id=sender_id, timestamp=datetime.utcnow())
#         session.add(message)
#         session.commit()
#         session.refresh(message)
#         return message

# def get_message_by_id(message_id: int):
#     with SessionLocal() as session:
#         return session.query(Message).filter(Message.message_id == message_id).first()

# def delete_message(message_id: int):
#     with SessionLocal() as session:
#         message = session.query(Message).filter(Message.message_id == message_id).first()
#         if message:
#             session.delete(message)
#             session.commit()
#             return True
#         return False

# # Example function for getting top chatrooms
# def get_top_chatrooms():
#     with SessionLocal() as session:
#         result = (
#             session.query(
#                 RoomUser.room_id,
#                 func.sum(User.user_xp).label('total_xp')
#             )
#             .join(User, User.user_id == RoomUser.user_id)
#             .group_by(RoomUser.room_id)
#             .order_by(desc('total_xp'))
#             .limit(5)
#             .all()
#         )
#         return result
# # Base = declarative_base()

# # # Enum for message types if needed
# # class ProfileImageTargetEnum(enum.Enum):
# #     chattingroom = "chattingroom"
# #     user = "user"


# # Base = declarative_base()

# # class ChattingRoom(Base):
# #     __tablename__ = 'chatting_rooms'

# #     room_id = Column(Integer, primary_key=True)
# #     profile_image_id = Column(Integer, ForeignKey('profile_image.profile_image_id'), nullable=False)
# #     room_type = Column(String(45), nullable=False)
# #     room_name = Column(String(45), nullable=False)
# #     room_manager = Column(BigInteger, nullable=False)
# #     room_create = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
# #     room_total_users = Column(Integer, nullable=False)

# #     # Relationship (if needed)
# #     # profile_image = relationship('ProfileImage', back_populates='chatting_rooms')

# # # # Assuming ProfileImage class is defined as follows:
# # # class ProfileImage(Base):
# # #     __tablename__ = 'profile_image'

# # #     profile_image_id = Column(Integer, primary_key=True, autoincrement=True)
# # #     # Other fields...

# # #     chatting_rooms = relationship('ChattingRoom', back_populates='profile_image')



# # # class Hashtag(Base):
# # #     __tablename__ = 'hashtag'

# # #     hashtag_id = Column(Integer, primary_key=True, autoincrement=True)
# # #     room_id = Column(Integer, ForeignKey('chatting_rooms.room_id'), nullable=False)  # 수정
# # #     tag = Column(String(255), nullable=False)

# #     # Relationship back to ChattingRoom
# #     # chatting_room = relationship("ChattingRoom", back_populates="hashtag")

# # class Message(Base):
# #     __tablename__ = 'message'

# #     message_id = Column(Integer, primary_key=True, autoincrement=True)
# #     room_id = Column(Integer, ForeignKey('chatting_room.room_id'), nullable=False)
# #     sender_id = Column(BigInteger, nullable=False)
# #     timestamp = Column(DateTime, default=datetime.utcnow)

# #     # Relationships with different message types
# #     images = relationship("MessageImage", back_populates="message")
# #     reads = relationship("MessageRead", back_populates="message")
# #     texts = relationship("MessageText", back_populates="message")
# #     videos = relationship("MessageVideo", back_populates="message")
# #     voices = relationship("MessageVoice", back_populates="message")

# #     # Relationship back to ChattingRoom
# #     chatting_room = relationship("ChattingRoom", back_populates="message")

# # class MessageImage(Base):
# #     __tablename__ = 'message_image'

# #     image_id = Column(Integer, primary_key=True, autoincrement=True)
# #     message_id = Column(Integer, ForeignKey('message.message_id'), nullable=False)
# #     url = Column(String(255), nullable=False)

# #     # Relationship back to Message
# #     message = relationship("Message", back_populates="images")

# # class MessageRead(Base):
# #     __tablename__ = 'message_read'

# #     read_id = Column(Integer, primary_key=True, autoincrement=True)
# #     message_id = Column(Integer, ForeignKey('message.message_id'), nullable=False)
# #     user_id = Column(BigInteger, nullable=False)
# #     read_timestamp = Column(DateTime, default=datetime.utcnow)

# #     # Relationship back to Message
# #     message = relationship("Message", back_populates="reads")

# # class MessageText(Base):
# #     __tablename__ = 'message_text'

# #     text_id = Column(Integer, primary_key=True, autoincrement=True)
# #     message_id = Column(Integer, ForeignKey('message.message_id'), nullable=False)
# #     content = Column(String(255), nullable=False)

# #     # Relationship back to Message
# #     message = relationship("Message", back_populates="texts")

# # class MessageVideo(Base):
# #     __tablename__ = 'message_video'

# #     video_id = Column(Integer, primary_key=True, autoincrement=True)
# #     message_id = Column(Integer, ForeignKey('message.message_id'), nullable=False)
# #     url = Column(String(255), nullable=False)

# #     # Relationship back to Message
# #     message = relationship("Message", back_populates="videos")

# # class MessageVoice(Base):
# #     __tablename__ = 'message_voice'

# #     voice_id = Column(Integer, primary_key=True, autoincrement=True)
# #     message_id = Column(Integer, ForeignKey('message.message_id'), nullable=False)
# #     url = Column(String(255), nullable=False)

# #     # Relationship back to Message
# #     message = relationship("Message", back_populates="voices")


# # # ChattingRoom CRUD
# # def create_chatting_room(room_id,profile_image_id,room_type,room_name,room_manager,room_total_users):
# #     with SessionLocal() as session:
# #         new_room = ChattingRoom(
# #             room_id=room_id,
# #             profile_image_id=profile_image_id,
# #             room_type=room_type,
# #             room_name=room_name,
# #             room_manager=room_manager,
# #             room_total_users=room_total_users,
# #             room_create=datetime.utcnow()
# #         )
# #         session.add(new_room)
# #         session.commit()
# #         session.refresh(new_room)
# #         return new_room
# #         room = ChattingRoom()
# #         session.add(room)
# #         session.commit()
# #         session.refresh(room)
# #         return room

# # def get_chatting_room_by_id(room_id: int):
# #     with SessionLocal() as session:
# #         return session.query(ChattingRoom).filter(ChattingRoom.room_id == room_id).first()

# # def update_chatting_room(room_id: int):
# #     with SessionLocal() as session:
# #         room = session.query(ChattingRoom).filter(ChattingRoom.room_id == room_id).first()
# #         # todo something
# #         if room:
# #             session.commit()
# #             session.refresh(room)
# #         return room

# # def delete_chatting_room(room_id: int):
# #     with SessionLocal() as session:
# #         room = session.query(ChattingRoom).filter(ChattingRoom.room_id == room_id).first()
# #         if room:
# #             session.delete(room)
# #             session.commit()
# #             return True
# #         return False

# # # Hashtag CRUD
# # # def create_hashtag(room_id: int, tag: str):
# # #     with SessionLocal() as session:
# # #         hashtag = Hashtag(room_id=room_id, tag=tag)
# # #         session.add(hashtag)
# # #         session.commit()
# # #         session.refresh(hashtag)
# # #         return hashtag

# # # def get_hashtag_by_id(hashtag_id: int):
# # #     with SessionLocal() as session:
# # #         return session.query(Hashtag).filter(Hashtag.hashtag_id == hashtag_id).first()

# # # def delete_hashtag(hashtag_id: int):
# # #     with SessionLocal() as session:
# # #         hashtag = session.query(Hashtag).filter(Hashtag.hashtag_id == hashtag_id).first()
# # #         if hashtag:
# # #             session.delete(hashtag)
# # #             session.commit()
# # #             return True
# # #         return False

# # # Message CRUD
# # def create_message(room_id: int, sender_id: int):
# #     with SessionLocal() as session:
# #         message = Message(room_id=room_id, sender_id=sender_id, timestamp=datetime.utcnow())
# #         session.add(message)
# #         session.commit()
# #         session.refresh(message)
# #         return message

# # def get_message_by_id(message_id: int):
# #     with SessionLocal() as session:
# #         return session.query(Message).filter(Message.message_id == message_id).first()

# # def delete_message(message_id: int):
# #     with SessionLocal() as session:
# #         message = session.query(Message).filter(Message.message_id == message_id).first()
# #         if message:
# #             session.delete(message)
# #             session.commit()
# #             return True
# #         return False

# # # MessageImage CRUD
# # def create_message_image(message_id: int, url: str):
# #     with SessionLocal() as session:
# #         image = MessageImage(message_id=message_id, url=url)
# #         session.add(image)
# #         session.commit()
# #         session.refresh(image)
# #         return image

# # def get_message_image_by_id(image_id: int):
# #     with SessionLocal() as session:
# #         return session.query(MessageImage).filter(MessageImage.image_id == image_id).first()

# # def delete_message_image(image_id: int):
# #     with SessionLocal() as session:
# #         image = session.query(MessageImage).filter(MessageImage.image_id == image_id).first()
# #         if image:
# #             session.delete(image)
# #             session.commit()
# #             return True
# #         return False

# # # MessageRead CRUD
# # def create_message_read(message_id: int, user_id: int):
# #     with SessionLocal() as session:
# #         read = MessageRead(message_id=message_id, user_id=user_id, read_timestamp=datetime.utcnow())
# #         session.add(read)
# #         session.commit()
# #         session.refresh(read)
# #         return read

# # def get_message_read_by_id(read_id: int):
# #     with SessionLocal() as session:
# #         return session.query(MessageRead).filter(MessageRead.read_id == read_id).first()

# # def delete_message_read(read_id: int):
# #     with SessionLocal() as session:
# #         read = session.query(MessageRead).filter(MessageRead.read_id == read_id).first()
# #         if read:
# #             session.delete(read)
# #             session.commit()
# #             return True
# #         return False

# # # MessageText CRUD
# # def create_message_text(message_id: int, content: str):
# #     with SessionLocal() as session:
# #         text = MessageText(message_id=message_id, content=content)
# #         session.add(text)
# #         session.commit()
# #         session.refresh(text)
# #         return text

# # def get_message_text_by_id(text_id: int):
# #     with SessionLocal() as session:
# #         return session.query(MessageText).filter(MessageText.text_id == text_id).first()

# # def delete_message_text(text_id: int):
# #     with SessionLocal() as session:
# #         text = session.query(MessageText).filter(MessageText.text_id == text_id).first()
# #         if text:
# #             session.delete(text)
# #             session.commit()
# #             return True
# #         return False

# # # MessageVideo CRUD
# # def create_message_video(message_id: int, url: str):
# #     with SessionLocal() as session:
# #         video = MessageVideo(message_id=message_id, url=url)
# #         session.add(video)
# #         session.commit()
# #         session.refresh(video)
# #         return video

# # def get_message_video_by_id(video_id: int):
# #     with SessionLocal() as session:
# #         return session.query(MessageVideo).filter(MessageVideo.video_id == video_id).first()

# # def delete_message_video(video_id: int):
# #     with SessionLocal() as session:
# #         video = session.query(MessageVideo).filter(MessageVideo.video_id == video_id).first()
# #         if video:
# #             session.delete(video)
# #             session.commit()
# #             return True
# #         return False

# # # MessageVoice CRUD
# # def create_message_voice(message_id: int, url: str):
# #     with SessionLocal() as session:
# #         voice = MessageVoice(message_id=message_id, url=url)
# #         session.add(voice)
# #         session.commit()
# #         session.refresh(voice)
# #         return voice

# # def get_message_voice_by_id(voice_id: int):
# #     with SessionLocal() as session:
# #         return session.query(MessageVoice).filter(MessageVoice.voice_id == voice_id).first()

# # def delete_message_voice(voice_id: int):
# #     with SessionLocal() as session:
# #         voice = session.query(MessageVoice).filter(MessageVoice.voice_id == voice_id).first()
# #         if voice:
# #             session.delete(voice)
# #             session.commit()
# #             return True
# #         return False



# # def get_all_chatting_rooms(session: Session) -> List[ChattingRoom]:
# #     return session.query(ChattingRoom).all()



# # # 예시로 session을 생성하는 함수입니다. 실제 세션 관리 방법에 맞게 수정하세요.
# # def get_top_chatrooms():
# #     with SessionLocal() as session:
# #         # `chatroom_code`별 `xp` 합계를 구하고, 상위 5개를 가져옴
# #         result = (
# #             session.query(
# #                 RoomUser.room_id,
# #                 func.sum(User.user_xp).label('total_xp')
# #             )
# #             .join(User, User.user_id == RoomUser.user_id)  # users 테이블과 조인
# #             .group_by(RoomUser.room_id)  # chatroom_code별로 그룹화
# #             .order_by(desc('total_xp'))  # xp 합계 내림차순으로 정렬
# #             .limit(5)  # 상위 5개만 선택
# #             .all()
# #         )
# #         return result
