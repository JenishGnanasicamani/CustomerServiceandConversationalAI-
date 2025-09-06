from fastapi import Depends
from .db import get_collection

async def messages_collection():
    return get_collection()