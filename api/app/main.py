from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .schemas import ChatRequest, ChatResponse, HistoryResponse, HealthResponse
from .db import get_collection
from .agents.graph import app_graph

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins= ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", response_model=HealthResponse)
async def health():
    return {"status": "ok", "model": settings.OLLAMA_MODEL}

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    coll = get_collection()
    await coll.insert_one({
        "session_id": req.session_id,
        "role": "user",
        "text": req.message,
    })

    result = await app_graph.ainvoke({
        "input": req.message,
    })
    reply = result["output"]

    await coll.insert_one({
        "session_id": req.session_id,
        "role": "assistant",
        "text": reply,
    })

    return {"session_id": req.session_id, "reply": reply}

@app.get("/history/{session_id}", response_model=HistoryResponse)
async def history(session_id: str):
    coll = get_collection()
    cursor = coll.find({"session_id": session_id}).sort("_id", 1)
    data = [
        {"role": d.get("role"), "text": d.get("text")} async for d in cursor
    ]
    return {"session_id": session_id, "messages": data}