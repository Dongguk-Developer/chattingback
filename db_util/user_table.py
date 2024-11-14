
# # from . import connect
# from sqlalchemy import create_engine, Column, Integer, String,BigInteger,Enum,DateTime,ForeignKey, TIMESTAMP,union_all,select, Table
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import relationship,aliased
# from sqlalchemy.exc import IntegrityError

# import enum
# from datetime import datetime
# # import db_session
# from db_util.db_session import SessionLocal
# from db_util.kakao_api import KakaoAPI
# from db_util.profile_image import ProfileImage
# from db_util import *
# # session = db_session
# Base = declarative_base()

# class User(Base):
#     __tablename__ = 'users'
    
#     user_id = Column(BigInteger, primary_key=True, nullable=False)
#     k_id = Column(BigInteger, ForeignKey(KakaoAPI.k_id), nullable=False)
#     profile_image_id = Column(Integer, ForeignKey(ProfileImage.profile_image_id), nullable=False)
#     user_nickname = Column(String(45, collation='utf8mb4_general_ci'), nullable=False)
#     user_xp = Column(Integer, nullable=False)
#     user_PI_argree = Column(String(10, collation='utf8mb4_general_ci'), nullable=False)
#     user_create = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
#     user_update = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
#     user_age = Column(Integer, nullable=False)
#     user_mbti = Column(String(45, collation='utf8mb4_general_ci'), default=None)
#     user_job = Column(String(45, collation='utf8mb4_general_ci'), default=None)
#     user_study_field = Column(String(45, collation='utf8mb4_general_ci'), default=None)

#     # Relationships
#     # k_id = relationship(KakaoAPI, back_populates="k_id")
#     # profile_image = relationship("ProfileImage", back_populates="users")
#     def __repr__(self):
#         return (f"<User(user_id={self.user_id}, k_id={self.k_id}, profile_image_id={self.profile_image_id}, "
#                 f"user_nickname='{self.user_nickname}', user_xp={self.user_xp}, user_PI_argree='{self.user_PI_argree}', "
#                 f"user_create={self.user_create}, user_update={self.user_update}, user_age={self.user_age}, "
#                 f"user_mbti='{self.user_mbti}', user_job='{self.user_job}', user_study_field='{self.user_study_field}')>")

# def create_user(user_id,k_id, profile_image_id, user_nickname, user_xp, user_PI_argree, user_age, user_mbti=None, user_job=None, user_study_field=None):
#     with SessionLocal() as session:
#         try:
#             new_user = User(
#                 user_id=user_id
#                 k_id=k_id,
#                 profile_image_id=profile_image_id,
#                 user_nickname=user_nickname,
#                 user_xp=user_xp,
#                 user_PI_argree=user_PI_argree,
#                 user_create=datetime.utcnow(),
#                 user_update=datetime.utcnow(),
#                 user_age=user_age,
#                 user_mbti=user_mbti,
#                 user_job=user_job,
#                 user_study_field=user_study_field
#             )
#             session.add(new_user)
#             session.commit()
#             session.refresh(new_user)
#             print(f"User created with ID: {new_user.user_id}")
#             return new_user
#         except IntegrityError as e:
#             session.rollback()
#             print("Error: Integrity constraint violated.", e)
#         finally:
#             session.close()

# def get_all_users():
#     with SessionLocal() as session:
#         users = session.query(User).all()
#         for user in users:
#             print(user)
#         return users


# def get_user_by_id(user_id):
#     with SessionLocal() as session:
#         user = session.query(User).filter(User.user_id == user_id).first()
#         if user:
#             print(f"User found: {user}")
#         else:
#             print("User not found.")
#         return user

# def get_user_with_profile_image(user_id):
#     with SessionLocal() as session:
#         try:
#             session.query(User)
#             # result = session.query(User).join(ProfileImage, User.profile_image_id == ProfileImage.profile_image_id).filter(User.user_id == user_id).one_or_none()
#             result = session.query(ProfileImage).join(User, User.profile_image_id == ProfileImage.profile_image_id).filter(User.user_id == user_id).order_by(ProfileImage.profile_image_create).one_or_none()
#             if result:
#                 return result
#             else:
#                 return None
#         except Exception as e:
#             print("=================================================================================",e)
# def update_user(user_id, user_nickname=None, user_xp=None, user_PI_argree=None, user_age=None, user_mbti=None, user_job=None, user_study_field=None,profile_image_id=None):
#     with SessionLocal() as session:
#         try:
#             user = session.query(User).filter(User.user_id == user_id).first()
#             if user:
#                 if user_nickname is not None:
#                     user.user_nickname = user_nickname
#                 if user_xp is not None:
#                     user.user_xp = user_xp
#                 if user_PI_argree is not None:
#                     user.user_PI_argree = user_PI_argree
#                 if user_age is not None:
#                     user.user_age = user_age
#                 if user_mbti is not None:
#                     user.user_mbti = user_mbti
#                 if user_job is not None:
#                     user.user_job = user_job
#                 if user_study_field is not None:
#                     user.user_study_field = user_study_field
#                 if profile_image_id is not None:
#                     user.profile_image_id = profile_image_id
#                 user.user_update = datetime.utcnow()

#                 session.commit()
#                 print(f"User updated: {user}")
#                 return user
#             else:
#                 print("User not found.")
#         except Exception as e:
#             print(114,e)


# def delete_user(user_id):
#     with SessionLocal() as session:
#         user = session.query(User).filter(User.user_id == user_id).first()
#         if user:
#             session.delete(user)
#             session.commit()
#             print(f"User deleted with ID: {user_id}")
#             return True
#         else:
#             print("User not found.")
#             return False

# """
# # Create a new user
# new_user = create_user(
#     k_id=1,
#     profile_image_id=1,
#     user_nickname="test_user",
#     user_xp=100,
#     user_PI_argree="yes",
#     user_age=25,
#     user_mbti="INTJ",
#     user_job="Developer",
#     user_study_field="Computer Science"
# )

# # Get all users
# all_users = get_all_users()

# # Get user by ID
# user = get_user_by_id(new_user.user_id)

# # Update user
# updated_user = update_user(new_user.user_id, user_xp=200, user_job="Senior Developer")

# # Delete user
# delete_success = delete_user(new_user.user_id)
# """


# from . import connect
from sqlalchemy import create_engine, Column, Integer, String,BigInteger,Enum,DateTime,ForeignKey, TIMESTAMP,union_all,select, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship,aliased
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc,asc, or_
import enum
from datetime import datetime
# import db_session
from db_util.db_session import SessionLocal
from db_util.kakao_api import KakaoAPI
from db_util.profile_image import ProfileImage
from .models import User
# session = db_session
Base = declarative_base()


def create_user(user_id,k_id, profile_image_id, user_nickname, user_xp, user_PI_argree, user_age, user_mbti=None, user_job=None, user_study_field=None):
    with SessionLocal() as session:
        try:
            new_user = User(
                user_id=user_id,
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
                user_study_field=user_study_field
            )
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            print(f"User created with ID: {new_user.user_id}")
            return new_user
        except IntegrityError as e:
            session.rollback()
            print("\n\n\n\n\nError: Integrity constraint violated.", e,"\n\n\n\n\n\n")
        finally:
            session.close()

def get_all_users():
    with SessionLocal() as session:
        users = session.query(User).all()
        for user in users:
            print(user)
        return users


def get_user_by_id(user_id):
    with SessionLocal() as session:
        user = session.query(User).filter(User.user_id == user_id).first()
        if user:
            print(f"User found: {user}")
        else:
            print("User not found.")
        return user

def get_user_with_profile_image(user_id):
    with SessionLocal() as session:
        try:
            # left_join_query = (
            #     session.query(ProfileImage, User)
            #     .outerjoin(User, User.profile_image_id == ProfileImage.profile_image_id)
            #     .filter(or_(User.user_id == user_id, User.user_id.is_(None)))
            # )
            # # RIGHT JOIN 부분
            join_query = (
                session.query(ProfileImage, User)
                .outerjoin(ProfileImage, ProfileImage.profile_image_id == User.profile_image_id)
                .filter(or_(ProfileImage.profile_image_id.isnot(None), User.user_id == user_id))
            )
            # print("leftjq",left_join_query.first())
            # print("rightjq",right_join_query.first())

            # LEFT JOIN과 RIGHT JOIN을 UNION으로 결합하여 FULL OUTER JOIN과 같은 효과
            # full_join_query = left_join_query.union(right_join_query)

            # result = full_join_query.order_by(desc(ProfileImage.profile_image_create)).first()
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
def update_user(user_id, user_nickname=None, user_xp=None, user_PI_argree=None, user_age=None, user_mbti=None, user_job=None, user_study_field=None,profile_image_id=None):
    with SessionLocal() as session:
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
                if user_study_field is not None:
                    user.user_study_field = user_study_field
                if profile_image_id is not None:
                    user.profile_image_id = profile_image_id
                user.user_update = datetime.utcnow()

                session.commit()
                print(f"User updated: {user}")
                return user
            else:
                print("User not found.")
        except IntegrityError as e:
            session.rollback()
            print("IntegrityError occurred:", e)
        except Exception as e:
            session.rollback()
            print("Error occurred:", e)


def delete_user(user_id):
    with SessionLocal() as session:
        user = session.query(User).filter(User.user_id == user_id).first()
        if user:
            session.delete(user)
            session.commit()
            print(f"User deleted with ID: {user_id}")
            return True
        else:
            print("User not found.")
            return False

def increase_user_xp(user_id):
    with SessionLocal() as session:
        try:
            user = session.query(User).filter(User.user_id == user_id).first()
            if user:
                user.user_xp += 1
                user.user_update = datetime.utcnow()
                session.commit()
                return user
            else:
                print("User not found.")
        except IntegrityError as e:
            session.rollback()
            print("IntegrityError occurred:", e)
        except Exception as e:
            session.rollback()
            print("Error occurred:", e)

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
    user_study_field="Computer Science"
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
