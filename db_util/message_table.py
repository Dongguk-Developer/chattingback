from db_util.db_session import SessionLocal
from .models import ChattingRoom,User,Message
def ensure_user_exists(user_id: int):
    with SessionLocal() as session:
        user = session.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise ValueError(f"User with user_id={user_id} does not exist.")
def ensure_room_exists(room_id: int):
    with SessionLocal() as session:
        room = session.query(ChattingRoom).filter(ChattingRoom.room_id == room_id).first()
        if not room:
            raise ValueError(f"Room with room_id={room_id} does not exist.")

def create_message(message_id: int, user_id: int, room_id: int, message_type: str):
    with SessionLocal() as session:
        try:
            # 유효성 검사
            ensure_user_exists(user_id)
            ensure_room_exists(room_id)

            new_message = Message(
                message_id=message_id,
                user_id=user_id,
                room_id=room_id,
                message_type=message_type,
                message_delete=0,
            )

            session.add(new_message)
            session.commit()
            session.refresh(new_message)
            return new_message

        except ValueError as e:
            print(f"Validation Error: {e}")
            raise
        except Exception as e:
            session.rollback()
            print(f"Error in create_message: {e}")
            raise


def get_message_by_id(message_id: int):
    with SessionLocal() as session:
        return session.query(Message).filter(Message.message_id == message_id).first()

def get_messages_by_room(room_id: int):
    with SessionLocal() as session:
        return session.query(Message).filter(Message.room_id == room_id).all()

def update_message_delete_status(message_id: int, delete_status: bool):
    with SessionLocal() as session:
        message = session.query(Message).filter(Message.message_id == message_id).first()
        if message:
            message.message_delete = delete_status
            session.commit()
            session.refresh(message)
        return message

def delete_message(message_id: int):
    with SessionLocal() as session:
        message = session.query(Message).filter(Message.message_id == message_id).first()
        if message:
            session.delete(message)
            session.commit()
            return True
        return False