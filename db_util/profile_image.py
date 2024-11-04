from sqlalchemy import create_engine, Column, Integer, String,BigInteger,Enum,DateTime,ForeignKey, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
import enum
from urllib.parse import quote_plus
from datetime import datetime
from db_util.db_session import SessionLocal



Base = declarative_base()



class ProfileImageTargetEnum(enum.Enum):
    chattingroom = "chattingroom"
    user = "user"

class ProfileImage(Base):
    __tablename__ = 'proflie_image'
    
    profile_image_id = Column(Integer, primary_key=True, autoincrement=True)
    profile_image_target = Column(Enum(ProfileImageTargetEnum), nullable=False)
    target_id = Column(BigInteger, nullable=False)
    profile_image_url = Column(String(255, collation='utf8mb4_general_ci'), nullable=False)
    profile_image_create = Column(String(255, collation='utf8mb4_general_ci'), nullable=False)

    def __repr__(self):
        return (f"<ProfileImage(profile_image_id={self.profile_image_id}, "
                f"profile_image_target={self.profile_image_target}, target_id={self.target_id}, "
                f"profile_image_url='{self.profile_image_url}', profile_image_create='{self.profile_image_create}')>")

# Create a new ProfileImage
def create_profile_image(profile_image_target, target_id, profile_image_url, profile_image_create):
    session = SessionLocal()
    try:
        new_profile_image = ProfileImage(
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

# Read ProfileImage by ID
def get_profile_image_by_id(profile_image_id: int):
    session = SessionLocal()
    profile_image = session.query(ProfileImage).filter(ProfileImage.profile_image_id == profile_image_id).first()
    if profile_image:
        return profile_image
    else:
        print(f"ProfileImage with id {profile_image_id} not found.")
        return None

# Update ProfileImage
def update_profile_image(profile_image_id: int, **kwargs):
    session = SessionLocal()
    profile_image = get_profile_image_by_id(session, profile_image_id)
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

# Delete ProfileImage
def delete_profile_image(profile_image_id: int):
    session = SessionLocal()
    profile_image = get_profile_image_by_id(session, profile_image_id)
    if profile_image:
        session.delete(profile_image)
        session.commit()
        print(f"Deleted ProfileImage with id: {profile_image_id}")
        return profile_image
    else:
        print("ProfileImage not found.")
        return None