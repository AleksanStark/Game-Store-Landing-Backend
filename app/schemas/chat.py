from pydantic import BaseModel
from datetime import datetime
 
 
class GuestOut(BaseModel):
    guest_id: str
 
 
class MessageOut(BaseModel):
    id: int
    guest_id: str
    sender: str
    body: str
    read_at: datetime | None
    created_at: datetime
 
 
class ConversationOut(BaseModel):
    guest_id: str
    last_seen_at: datetime
    last_message: str | None
    last_sender: str | None
    last_message_at: datetime | None
    unread_count: int
 