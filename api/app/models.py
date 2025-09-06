from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class Message(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    session_id: str
    role: str  # user | assistant | system
    text: str
    created_at: datetime = Field(default_factory=datetime.utcnow)