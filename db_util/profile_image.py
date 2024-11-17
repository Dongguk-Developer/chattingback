from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError
from db_util.db_session import SessionLocal
from .models import ProfileImage


Base = declarative_base()

def create_profile_image(profile_image_id,profile_image_target, target_id, profile_image_url, profile_image_create):
    with SessionLocal() as session:
        try:
            new_profile_image = ProfileImage(
                profile_image_id=profile_image_id,
                profile_image_target=profile_image_target,
                target_id=target_id,
                profile_image_url=profile_image_url,
                profile_image_create=profile_image_create
            )
            session.add(new_profile_image)
            session.commit()
            session.refresh(new_profile_image)
            print(f"Inserted ProfileImage with id: {new_profile_image.profile_image_id}")
            return new_profile_image
        except IntegrityError as e:
            session.rollback()
            print("IntegrityError occurred:", e)
        except Exception as e:
            session.rollback()
            print("Error occurred:", e)

def get_profile_image_by_id(profile_image_id: int):
    with SessionLocal() as session:
        try:
            profile_image = session.query(ProfileImage).filter(ProfileImage.profile_image_id == profile_image_id).first()
            if profile_image:
                return profile_image
            else:
                print(f"ProfileImage with id {profile_image_id} not found.")
                return None
        except IntegrityError as e:
            session.rollback()
            print("IntegrityError occurred:", e)
        except Exception as e:
            session.rollback()
            print("Error occurred:", e)

def update_profile_image(profile_image_id: int, **kwargs):
    with SessionLocal() as session:
        profile_image = get_profile_image_by_id(profile_image_id)
        if profile_image:
            for key, value in kwargs.items():
                if hasattr(profile_image, key):
                    setattr(profile_image, key, value)
            session.commit()
            session.refresh(profile_image)
            print(f"Updated ProfileImage with id: {profile_image_id}")
            return profile_image
        else:
            print("ProfileImage not found.")
            return None

def delete_profile_image(profile_image_id: int):
    with SessionLocal() as session:
        profile_image = get_profile_image_by_id(profile_image_id)
        if profile_image:
            session.delete(profile_image)
            session.commit()
            print(f"Deleted ProfileImage with id: {profile_image_id}")
            return profile_image
        else:
            print("ProfileImage not found.")
            return None