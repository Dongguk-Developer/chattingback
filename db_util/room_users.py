# from . import connect
from sqlalchemy import create_engine, Column, Integer, String,BigInteger,Enum,DateTime,ForeignKey, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
import enum
from urllib.parse import quote_plus
from datetime import datetime
from db_util.db_session import SessionLocal
from sqlalchemy import Column, Integer, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from .models import RoomUser,ChattingRoom,User,Hashtag



def get_user_chatrooms_with_hashtag(user_id):
    with SessionLocal() as session:
        try:

            join_query = (
                session.query(RoomUser, Hashtag)
                .outerjoin(ProfileImage, RoomUser.room_id == Hashtag.room_id)
                .filter(or_(ProfileImage.profile_image_id.isnot(None), User.user_id == user_id))
            )

            result = join_query.order_by(asc(ProfileImage.profile_image_create)).first()
            profile_image, user = result  # 튜플 언패킹
            print(result)
            result_dict = {
                "profile_image": {
                    "profile_image_id": profile_image.profile_image_id,
                    "profile_image_target": profile_image.profile_image_target.value,
                    "target_id": profile_image.target_id,
                    "profile_image_url": profile_image.profile_image_url,
                    "profile_image_create": str(profile_image.profile_image_create),
                } if profile_image else None,
                "user": {
                    "user_id": user.user_id,
                    "k_id": user.k_id,
                    "profile_image_id": user.profile_image_id,
                    "user_nickname": user.user_nickname,
                    "user_xp": user.user_xp,
                    "user_PI_argree": user.user_PI_argree,
                    "user_create": str(user.user_create),
                    "user_update": str(user.user_update),
                    "user_age": user.user_age,
                    "user_mbti": user.user_mbti,
                    "user_job": user.user_job,
                    "user_study_field": user.user_study_field,
                } if user else None
            }

            # 필요없는 필드 삭제
            # if "user" in result_dict:
            #     result_dict["profile_image"].pop("profile_image_id", None)
            #     result_dict["profile_image"].pop("profile_image_target", None)
            #     result_dict["profile_image"].pop("target_id", None)
            #     result_dict["profile_image"].pop("profile_image_create", None)
            #     result_dict["user"].pop("k_id", None)
            #     result_dict["user"].pop("profile_image_id", None)
            #     result_dict["user"].pop("user_xp", None)
            #     result_dict["user"].pop("user_PI_argree", None)
            #     result_dict["user"].pop("user_create", None)
            #     result_dict["user"].pop("user_update", None)
            result = result_dict
            if result:
                return result
            else:
                return None
        except IntegrityError as e:
            session.rollback()
            print("IntegrityError occurred:", e)
        except Exception as e:
            session.rollback()
            print("Error occurred:", e)
# Create (방에 유저 추가)
def create_room_user(room_id: int, user_id: int):
    with SessionLocal() as session:
        db_room_user = RoomUser(room_id=room_id, user_id=user_id)
        session.add(db_room_user)
        session.commit()
        session.refresh(db_room_user)
        return db_room_user

# Read (특정 방의 모든 유저 조회)
def get_users_in_room(room_id: int):
    with SessionLocal() as session:
        return session.query(RoomUser).filter(RoomUser.room_id == room_id).all()

# Read (특정 유저가 참여한 모든 방 조회)
def get_rooms_for_user(user_id: int):
    with SessionLocal() as session:
        return session.query(RoomUser).filter(RoomUser.user_id == user_id).all()

# Delete (방에서 유저 제거)
def delete_room_user(room_id: int, user_id: int):
    with SessionLocal() as session:
        db_room_user = session.query(RoomUser).filter(
            RoomUser.room_id == room_id, RoomUser.user_id == user_id
        ).first()
        if db_room_user:
            session.delete(db_room_user)
            session.commit()