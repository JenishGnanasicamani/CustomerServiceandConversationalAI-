from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    session_id: str
    reply: str

class HistoryResponse(BaseModel):
    session_id: str
    messages: List[dict]

class HealthResponse(BaseModel):
    status: str
    model: Optional[str] = None