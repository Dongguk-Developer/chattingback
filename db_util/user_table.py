from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from sqlalchemy.orm import joinedload

from db_util.db_session import SessionLocal
from .models import User,ProfileImage,RoomUser,Calendar,Message,MessageText,MessageImage,MessageRead,MessageVideo,MessageVoice,Planner
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
            return new_user
        except IntegrityError as e:
            session.rollback()
        finally:
            session.close()

def get_all_users():
    with SessionLocal() as session:
        users = session.query(User).all()
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
            user = session.query(User).options(joinedload(User.profile_image)).filter(User.user_id == user_id).first()
            if not user:
                return None
            profile_image = session.query(ProfileImage).filter(ProfileImage.profile_image_id == user.profile_image_id).first()
            return {
                "profile_image": {
                    "profile_image_id": profile_image.profile_image_id,
                    "profile_image_target": profile_image.profile_image_target.value,
                    "target_id": profile_image.target_id,
                    "profile_image_url": profile_image.profile_image_url,
                    "profile_image_create": str(profile_image.profile_image_create),
                },
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
                }
            }
            
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
        try:
            # Deleting from RoomUser table
            session.query(RoomUser).filter_by(user_id=user_id).delete()

            # Deleting messages from Message table
            messages = session.query(Message).filter_by(user_id=user_id).all()
            for message in messages:
                session.query(MessageImage).filter_by(message_id=message.message_id).delete()
                session.query(MessageText).filter_by(message_id=message.message_id).delete()
                session.query(MessageVideo).filter_by(message_id=message.message_id).delete()
                session.query(MessageVoice).filter_by(message_id=message.message_id).delete()
                session.query(MessageRead).filter_by(message_id=message.message_id).delete()
            session.query(Message).filter_by(user_id=user_id).delete()

            # Deleting from Planner table
            session.query(Planner).filter_by(user_id=user_id).delete()

            # Deleting from Calendar table
            session.query(Calendar).filter_by(user_id=user_id).delete()

            # Deleting user profile image
            user = session.query(User).filter_by(user_id=user_id).first()

            # Deleting user from User table
            session.query(User).filter_by(user_id=user_id).delete()
            if user and user.profile_image_id:
                session.query(ProfileImage).filter_by(profile_image_id=user.profile_image_id).delete()

            session.commit()
            print(f"All data related to user_id={user_id} has been successfully deleted.")
            return f"All data related to user_id={user_id} has been successfully deleted."

        except IntegrityError as e:
            session.rollback()
            print(f"Failed to delete data for user_id={user_id}: {str(e)}")
            return f"Failed to delete data for user_id={user_id}: {str(e)}"

        except Exception as e:
            session.rollback()
            print(f"An error occurred: {str(e)}")
            return f"An error occurred: {str(e)}"
        # user = session.query(User).filter(User.user_id == user_id).first()
        # if user:
        #     session.delete(user)
        #     session.commit()
        #     print(f"User deleted with ID: {user_id}")
        #     return True
        # else:
        #     print("User not found.")
        #     return False

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