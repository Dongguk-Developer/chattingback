
# from . import connect
from sqlalchemy import create_engine, Column, Integer, String,BigInteger,Enum,DateTime,ForeignKey, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError
import enum
from datetime import datetime
# import db_session
from db_util.db_session import SessionLocal
from db_util.kakao_api import KakaoAPI
from db_util.profile_image import ProfileImage
from db_util import *
# session = db_session
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(BigInteger, primary_key=True, autoincrement=True)
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
    user_stuty_field = Column(String(45, collation='utf8mb4_general_ci'), default=None)

    # Relationships
    # k_id = relationship(KakaoAPI, back_populates="k_id")
    # profile_image = relationship("ProfileImage", back_populates="users")
    def __repr__(self):
        return (f"<User(user_id={self.user_id}, k_id={self.k_id}, profile_image_id={self.profile_image_id}, "
                f"user_nickname='{self.user_nickname}', user_xp={self.user_xp}, user_PI_argree='{self.user_PI_argree}', "
                f"user_create={self.user_create}, user_update={self.user_update}, user_age={self.user_age}, "
                f"user_mbti='{self.user_mbti}', user_job='{self.user_job}', user_stuty_field='{self.user_stuty_field}')>")

def create_user(k_id, profile_image_id, user_nickname, user_xp, user_PI_argree, user_age, user_mbti=None, user_job=None, user_stuty_field=None):
    session = SessionLocal()
    try:
        new_user = User(
            k_id=k_id,
            profile_image_id=profile_image_id,
            user_nickname=user_nickname,
            user_xp=user_xp,
            user_PI_argree=user_PI_argree,
            user_create=datetime.utcnow(),
            user_update=datetime.utcnow(),
            user_age=user_age,
            user_mbti=user_mbti,
            user_job=user_job,
            user_stuty_field=user_stuty_field
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        print(f"User created with ID: {new_user.user_id}")
        return new_user
    except IntegrityError as e:
        session.rollback()
        print("Error: Integrity constraint violated.", e)
    finally:
        session.close()

def get_all_users():
    session = SessionLocal()
    try:
        users = session.query(User).all()
        for user in users:
            print(user)
        return users
    finally:
        session.close()

def get_user_by_id(user_id):
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.user_id == user_id).first()
        if user:
            print(f"User found: {user}")
        else:
            print("User not found.")
        return user
    finally:
        session.close()

def update_user(user_id, user_nickname=None, user_xp=None, user_PI_argree=None, user_age=None, user_mbti=None, user_job=None, user_stuty_field=None):
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.user_id == user_id).first()
        if user:
            if user_nickname is not None:
                user.user_nickname = user_nickname
            if user_xp is not None:
                user.user_xp = user_xp
            if user_PI_argree is not None:
                user.user_PI_argree = user_PI_argree
            if user_age is not None:
                user.user_age = user_age
            if user_mbti is not None:
                user.user_mbti = user_mbti
            if user_job is not None:
                user.user_job = user_job
            if user_stuty_field is not None:
                user.user_stuty_field = user_stuty_field
            user.user_update = datetime.utcnow()

            session.commit()
            print(f"User updated: {user}")
            return user
        else:
            print("User not found.")
    finally:
        session.close()

def delete_user(user_id):
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.user_id == user_id).first()
        if user:
            session.delete(user)
            session.commit()
            print(f"User deleted with ID: {user_id}")
            return True
        else:
            print("User not found.")
            return False
    finally:
        session.close()
"""
# Create a new user
new_user = create_user(
    k_id=1,
    profile_image_id=1,
    user_nickname="test_user",
    user_xp=100,
    user_PI_argree="yes",
    user_age=25,
    user_mbti="INTJ",
    user_job="Developer",
    user_stuty_field="Computer Science"
)

# Get all users
all_users = get_all_users()

# Get user by ID
user = get_user_by_id(new_user.user_id)

# Update user
updated_user = update_user(new_user.user_id, user_xp=200, user_job="Senior Developer")

# Delete user
delete_success = delete_user(new_user.user_id)
"""

