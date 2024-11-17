from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, TIMESTAMP, DateTime, SmallInteger,Enum,Date
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
import enum
import logging

# SQLAlchemy 로거 가져오기
logging.getLogger("sqlalchemy.engine").disabled = True
Base = declarative_base()

class KakaoAPI(Base):
    __tablename__ = 'kakao_api'
    
    k_id = Column(BigInteger, primary_key=True)
    kakao_id = Column(BigInteger, nullable=False)
    kakao_name = Column(String(45, collation='utf8mb4_general_ci'), nullable=False)
    kakao_tell = Column(String(45, collation='utf8mb4_general_ci'), nullable=False)
    kakao_email = Column(String(45, collation='utf8mb4_general_ci'), nullable=False)
    kakao_birth = Column(Integer, nullable=False)
    kakao_create = Column(DateTime, default=None)
    kakao_update = Column(DateTime, default=None)
    kakao_image = Column(String(255, collation='utf8mb4_general_ci'), default=None)
    kakao_refresh_token = Column(String(255, collation='utf8mb4_general_ci'), nullable=False)
    kakao_access_token = Column(String(255, collation='utf8mb4_general_ci'), nullable=False)

    def __repr__(self):
        return (f"<KakaoAPI(k_id={self.k_id}, kakao_id={self.kakao_id}, kakao_name='{self.kakao_name}', "
                f"kakao_tell='{self.kakao_tell}', kakao_email='{self.kakao_email}', kakao_birth={self.kakao_birth}, "
                f"kakao_create={self.kakao_create}, kakao_update={self.kakao_update}, kakao_image='{self.kakao_image}', "
                f"kakao_refresh_token='{self.kakao_refresh_token}', kakao_access_token='{self.kakao_access_token}')>")
class ProfileImageTargetEnum(enum.Enum):
    chattingroom = "chattingroom"
    user = "user"

class ProfileImage(Base):
    __tablename__ = 'profile_image'
    
    profile_image_id = Column(Integer, primary_key=True, nullable=False)
    profile_image_target = Column(Enum(ProfileImageTargetEnum), nullable=False)
    target_id = Column(BigInteger, nullable=False)
    profile_image_url = Column(String(255, collation='utf8mb4_general_ci'), nullable=False)
    profile_image_create = Column(String(255, collation='utf8mb4_general_ci'), nullable=False)

    def __repr__(self):
        return (f"<ProfileImage(profile_image_id={self.profile_image_id}, "
                f"profile_image_target={self.profile_image_target}, target_id={self.target_id}, "
                f"profile_image_url='{self.profile_image_url}', profile_image_create='{self.profile_image_create}')>")
class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(BigInteger, primary_key=True)
    k_id = Column(BigInteger, ForeignKey(KakaoAPI.k_id), nullable=False)
    profile_image_id = Column(Integer, ForeignKey(ProfileImage.profile_image_id), nullable=False)
    user_nickname = Column(String(45, collation='utf8mb4_general_ci'), nullable=False)
    user_xp = Column(Integer, nullable=False)
    user_PI_argree = Column(String(10, collation='utf8mb4_general_ci'), nullable=False)
    user_create = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    user_update = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_age = Column(Integer, nullable=False)
    user_mbti = Column(String(45, collation='utf8mb4_general_ci'), default=None)
    user_job = Column(String(45, collation='utf8mb4_general_ci'), default=None)
    user_study_field = Column(String(45, collation='utf8mb4_general_ci'), default=None)
    profile_image = relationship("ProfileImage", backref="user", foreign_keys=[profile_image_id])
    def __repr__(self):
        return (f"<User(user_id={self.user_id}, k_id={self.k_id}, profile_image_id={self.profile_image_id}, "
                f"user_nickname='{self.user_nickname}', user_xp={self.user_xp}, user_PI_argree='{self.user_PI_argree}', "
                f"user_create={self.user_create}, user_update={self.user_update}, user_age={self.user_age}, "
                f"user_mbti='{self.user_mbti}', user_job='{self.user_job}', user_study_field='{self.user_study_field}')>")

    profile_image = relationship("ProfileImage", backref="user")

class Planner(Base):
    __tablename__ = 'planner'

    planner_id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey(User.user_id), nullable=False)
    planner_date = Column(Date, nullable=False)
    planner_schedule_name = Column(String(60), nullable=False)
    planner_schedule_status = Column(String(45), nullable=True)


class Calendar(Base):
    __tablename__ = 'calender'

    calender_id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(BigInteger, ForeignKey('users.user_id'), nullable=False)
    calender_date_start = Column(Date, nullable=False)
    calender_date_finish = Column(Date, nullable=False)
    calender_schedule_name = Column(String(60), nullable=False)
    calender_schedule_memo = Column(String(60), nullable=True)
    calender_is_dday = Column(SmallInteger, nullable=False)

class ChattingRoom(Base):

    __tablename__ = 'chatting_rooms'

    room_id = Column(Integer, primary_key=True)
    profile_image_id = Column(Integer, ForeignKey(ProfileImage.profile_image_id), nullable=False)
    room_type = Column(String(45), nullable=False)
    room_name = Column(String(45), nullable=False)
    room_manager = Column(BigInteger, nullable=False)
    room_create = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    room_total_users = Column(Integer, nullable=False)
class Hashtag(Base):
    __tablename__ = 'hashtag'

    hashtag_id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey(ChattingRoom.room_id), nullable=False)
    hashtag_title = Column(String(255), nullable=False)

    def __repr__(self):
        return f"<Hashtag(hashtag_id={self.hashtag_id}, room_id={self.room_id}, hashtag_title='{self.hashtag_title}')>"
class MessageTypeEnum(enum.Enum):
    text = "text"
    image = "image"
    voice = "voice"
    video = "video"
class Message(Base):
    __tablename__ = 'message'

    message_id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey(ChattingRoom.room_id), nullable=False)
    user_id = Column(BigInteger, ForeignKey(User.user_id), nullable=False)
    message_create = Column(DateTime, default=datetime.utcnow)
    message_type = Column(Enum(MessageTypeEnum), nullable=False)
    message_delete = Column(SmallInteger, nullable=False)
    user = relationship("User", backref="messages")

class MessageImage(Base):
    __tablename__ = 'message_image'

    image_id = Column(Integer, primary_key=True)
    message_id = Column(Integer, ForeignKey(Message.message_id), nullable=False)
    url = Column(String(255), nullable=False)

class MessageRead(Base):
    __tablename__ = 'message_read'

    read_id = Column(Integer, primary_key=True)
    message_id = Column(Integer, ForeignKey(Message.message_id), nullable=False)
    user_id = Column(BigInteger, nullable=False)
    read_timestamp = Column(DateTime, default=datetime.utcnow)

class MessageText(Base):
    __tablename__ = 'message_text'

    message_text_id = Column(Integer, primary_key=True)
    message_id = Column(Integer, ForeignKey(Message.message_id), nullable=False)
    message_text = Column(String(255), nullable=False)

class MessageVideo(Base):
    __tablename__ = 'message_video'

    video_id = Column(Integer, primary_key=True)
    message_id = Column(Integer, ForeignKey(Message.message_id), nullable=False)
    url = Column(String(255), nullable=False)

class MessageVoice(Base):
    __tablename__ = 'message_voice'

    voice_id = Column(Integer, primary_key=True)
    message_id = Column(Integer, ForeignKey(Message.message_id), nullable=False)
    url = Column(String(255), nullable=False)
Base = declarative_base()
class RoomUser(Base):

    __tablename__ = "room_users"

    room_id = Column(Integer, ForeignKey(ChattingRoom.room_id), primary_key=True)
    user_id = Column(BigInteger, ForeignKey(User.user_id), primary_key=True)