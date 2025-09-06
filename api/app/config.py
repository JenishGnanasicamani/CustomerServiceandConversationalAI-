import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl
from typing import List

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


    class Config:
        env_file = ".env"

settings = Settings()