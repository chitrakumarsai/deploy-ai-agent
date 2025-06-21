from sqlmodel import SQLModel, Field, DateTime
from datetime import datetime, timezone

def get_utc_now():
    return datetime.now().replace(tzinfo=timezone.utc)

class ChatMessagePayload(SQLModel):
    # pydantic Model
    # validation
    message: str

class ChatMessage(SQLModel, table = True):
    #database table
    #saving, updating, deleting, getting
    id:int | None = Field(default = None, primary_key = True)
    message: str
    created_at : datetime = Field(
        default_factory=None,
        sa_type= DateTime(timezone=True), # type: ignore
        primary_key=False,
        nullable= False
    )