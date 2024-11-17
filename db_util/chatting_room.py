from db_util.db_session import SessionLocal
from datetime import datetime
from typing import Optional
from sqlalchemy import func, desc
from sqlalchemy.sql import func
from .models import ChattingRoom,Message,Hashtag,ProfileImage,RoomUser,User


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

def get_top_chatrooms():
     with SessionLocal() as session:
        result = (
            session.query(
                RoomUser.room_id,
                func.sum(User.user_xp).label("total_xp"),
                ChattingRoom.room_manager,
                ChattingRoom.profile_image_id,
                ChattingRoom.room_total_users,
                ChattingRoom.room_name,
                ProfileImage.profile_image_url,
                func.group_concat(Hashtag.hashtag_title).label("hashtags")  # 그룹화된 해시태그
            )
            .join(User, RoomUser.user_id == User.user_id)
            .join(ChattingRoom, RoomUser.room_id == ChattingRoom.room_id)
            .join(ProfileImage, ChattingRoom.profile_image_id == ProfileImage.profile_image_id)
            .join(Hashtag,RoomUser.room_id ==Hashtag.room_id)
            .group_by(
                RoomUser.room_id,
                ChattingRoom.room_manager,
                ChattingRoom.profile_image_id,
                ChattingRoom.room_total_users,
                ChattingRoom.room_name,
                ProfileImage.profile_image_url,
                Hashtag.hashtag_title

            )
            .order_by(desc("total_xp"))
            .limit(5)
            .all()
        )

        top_chatrooms = [
            {
                "room_id": row.room_id,
                "total_xp": row.total_xp,
                "room_manager": row.room_manager,
                "profile_image_id": row.profile_image_id,
                "room_total_users": row.room_total_users,
                "room_name":row.room_name,
                "profile_image_url": row.profile_image_url,
                "hashtags": row.hashtags.split(",") if row.hashtags else [],  # Split by comma to get list
            }
            for row in result
        ]

        return top_chatrooms