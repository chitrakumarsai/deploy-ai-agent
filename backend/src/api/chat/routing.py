from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from .models import ChatMessagePayload , ChatMessage
from api.db import get_session

router = APIRouter()

@router.get("/")
def chat_health():
    return {"status": "ok" }


@router.get("/recent/")
def chat_list_messages(session: Session = Depends(get_session)):
    query = select(ChatMessage)
    result = session.exec(query).fetchall()[:10] # type: ignore

    return result

@router.post("/", response_model=ChatMessage)
def chat_create_message(
    payload: ChatMessagePayload,
    session: Session = Depends(get_session)
):
    data = payload.model_dump()
    obj = ChatMessage.model_validate(data)
    # ready to store in the database
    session.add(obj)
    session.commit()
    session.refresh(obj) # type: ignore
    return obj

