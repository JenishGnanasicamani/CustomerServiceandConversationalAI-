import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "CustomerServiceandConversationalAI"
    ENVIRONMENT: str = "development"

    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.1")

    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    MONGODB_DB: str = os.getenv("MONGODB_DB", "csai")
    MONGODB_COLLECTION: str = os.getenv("MONGODB_COLLECTION", "messages")

    KAFKA_TOPIC:str = os.getenv("KAFKA_TOPIC", "customer_conversation")
    KAFKA_BOOTSTRAP_SERVERS:str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
    KAFKA_GROUP_ID:str = os.getenv("KAFKA_GROUP_ID", "customer_conversation_consumer")
    KAFKA_MAX_MESSAGE_SIZE:int = int(os.getenv("KAFKA_MAX_MESSAGE_SIZE"))

    class Config:
        env_file = ".env"

settings = Settings()