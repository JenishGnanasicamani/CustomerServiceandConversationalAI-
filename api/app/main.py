import asyncio
import hashlib
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .schemas import ChatRequest, ChatResponse, HistoryResponse, HealthResponse
from .db import get_collection
from .agents.graph import app_graph
from aiokafka import AIOKafkaConsumer

consumer: AIOKafkaConsumer | None = None

def hash_message(msg: str) -> str:
    return hashlib.md5(msg.encode("utf-8")).hexdigest()

async def consume():
    global consumer
    consumer = AIOKafkaConsumer(
        settings.KAFKA_TOPIC,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id=settings.KAFKA_GROUP_ID,
        enable_auto_commit=True,
        auto_offset_reset="latest",
        max_partition_fetch_bytes=settings.KAFKA_MAX_MESSAGE_SIZE,
    )
    await consumer.start()
    try:
        async for msg in consumer:
            try:
                value = msg.value.decode("utf-8")
                await create_conversation(value)
            except Exception as e:
                print(f"Failed to process Kafka message: {e}")
    except asyncio.CancelledError:
        # Graceful shutdown
        print("Consumer task cancelled")
    finally:
        if consumer:
            await consumer.stop()
            print("Kafka consumer stopped")

async def create_conversation(data:str):
    #TODO:convert to conversation and store in db
    return None

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(consume())
    yield
    # shutdown
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(title=settings.PROJECT_NAME,lifespan=lifespan)

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

