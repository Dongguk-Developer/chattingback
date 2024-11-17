from sqlalchemy.orm import joinedload
from db_util.db_session import SessionLocal
from .models import RoomUser,ChattingRoom,User,Hashtag,Message,MessageText

def create_room_user(room_id: int, user_id: int):
    with SessionLocal() as session:
        db_room_user = RoomUser(room_id=room_id, user_id=user_id)
        session.add(db_room_user)
        session.commit()
        session.refresh(db_room_user)
        return db_room_user

def get_users_in_room(room_id: int):
    with SessionLocal() as session:
        return session.query(RoomUser).filter(RoomUser.room_id == room_id).all()
def get_hashtags_by_room_id(room_id: int):
    with SessionLocal() as session:
        return [i.hashtag_title for i in session.query(Hashtag).filter(Hashtag.room_id == room_id).all()]
def get_room_by_room_id(room_id:int):
    with SessionLocal() as session:
        
        return {"room":session.query(ChattingRoom).filter(ChattingRoom.room_id == room_id).one(),"hashtags":get_hashtags_by_room_id(room_id)}
def test(room_id:int):
    with SessionLocal() as session:
        # Query the Message table
        chats = (
            session.query(Message)
            .filter(Message.room_id == room_id)
            .options(
                joinedload(Message.user)  # Load the User model related to Message
                .joinedload(User.profile_image)  # Load the ProfileImage related to User
            )
            .all()
        )

        # Fetch related message_text data for each chat
        chat_data = []
        for chat in chats:
            # Query message_text table for the corresponding message_id
            message_text = (
                session.query(MessageText)
                .filter(MessageText.message_id == chat.message_id)
                .first()
            )

            chat_data.append({
                "message_id": chat.message_id,
                "room_id": chat.room_id,
                "user": {
                    "user_id": chat.user.user_id,
                    "user_nickname": chat.user.user_nickname,
                    "user_xp": chat.user.user_xp,
                    "user_mbti": chat.user.user_mbti,
                    "user_job": chat.user.user_job,
                    "user_study_field": chat.user.user_study_field,
                },
                "profile_image": {
                    "profile_image_url": chat.user.profile_image.profile_image_url,
                },
                "message": message_text.message_text if message_text else None,  # Use the content from message_text
                "message_create": chat.message_create,
                "message_delete": chat.message_delete,
            })

        return chat_data
def get_chat_by_room_id(room_id:int):
    with SessionLocal() as session:
        chats = (
            session.query(Message)
            .filter(Message.room_id == room_id)
            .filter(MessageText.message_id == chat.message_id)
            .options(
                joinedload(Message.user)  # Load the User model related to Message
                .joinedload(User.profile_image)  # Load the ProfileImage related to User
                .joinedload(MessageText.message_text)  # Load the ProfileImage related to User
                
            )
            .all()
        )
        chat_data = []
        for chat in chats:
            chat_data.append({
                "message_id": chat.message_id,
                "room_id": chat.room_id,
                "user": {
                    "user_id": chat.user.user_id,
                    "user_nickname": chat.user.user_nickname,
                    "user_xp": chat.user.user_xp,
                    "user_mbti": chat.user.user_mbti,
                    "user_job": chat.user.user_job,
                    "user_study_field": chat.user.user_study_field,
                },
                "profile_image": {
                    "profile_image_url": chat.user.profile_image.profile_image_url,
                },
                "message": chat.message_text,
                "message_create": chat.message_create,
                "message_delete": chat.message_delete,
            })
        return chat_data
def get_rooms_for_user_with_hashtags(user_id: int):
    with SessionLocal() as session:
        rooms = session.query(RoomUser).filter(RoomUser.user_id == user_id).all()
        result = []
        for room in rooms:
            hashtags = get_hashtags_by_room_id(room.room_id)
            title = get_room_by_room_id(room.room_id).room_name
            result.append({
                "title":title,
                "room_id": room.room_id,
                "user_id": room.user_id,
                "hashtags": hashtags
            })
        return result
def get_rooms_for_user(user_id: int):
    with SessionLocal() as session:
        return session.query(RoomUser).filter(RoomUser.user_id == user_id).all()

def delete_room_user(room_id: int, user_id: int):
    with SessionLocal() as session:
        db_room_user = session.query(RoomUser).filter(
            RoomUser.room_id == room_id, RoomUser.user_id == user_id
        ).first()
        if db_room_user:
            session.delete(db_room_user)
            session.commit()