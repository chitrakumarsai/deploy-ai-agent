from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from .models import ChatMessagePayload , ChatMessage
from api.auth import require_api_key
from api.db import get_session

RECENT_LIMIT = 10

router = APIRouter()

@router.get("/")
def chat_health():
    return {"status": "ok" }


@router.get("/recent/", dependencies=[Depends(require_api_key)])
def chat_list_messages(session: Session = Depends(get_session)):
    # Newest first, limited in the database rather than after loading every row.
    query = (
        select(ChatMessage)
        .order_by(ChatMessage.created_at.desc(), ChatMessage.id.desc())  # type: ignore
        .limit(RECENT_LIMIT)
    )
    return session.exec(query).all()

@router.post("/", response_model=ChatMessage, dependencies=[Depends(require_api_key)])
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

