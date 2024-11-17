from db_util.db_session import SessionLocal
from .models import MessageText

def create_message_text(text_id:int,message_id: int, text: str):
    with SessionLocal() as session:
        new_message_text = MessageText(
            message_text_id=text_id,
            message_id=message_id,
            message_text=text
        )
        session.add(new_message_text)
        session.commit()
        session.refresh(new_message_text)
        return new_message_text

def get_message_text_by_id(message_text_id: int):
    with SessionLocal() as session:
        return session.query(MessageText).filter(MessageText.message_text_id == message_text_id).first()

def get_message_text_by_message_id(message_id: int):
    with SessionLocal() as session:
        return session.query(MessageText).filter(MessageText.message_id == message_id).first()

def delete_message_text(message_text_id: int):
    with SessionLocal() as session:
        message_text = session.query(MessageText).filter(MessageText.message_text_id == message_text_id).first()
        if message_text:
            session.delete(message_text)
            session.commit()
            return True
        return False
