from typing import TypedDict

class ToolInput(TypedDict):
    query: str

def retrieve_kb(query: str) -> str:
    return f"(KB) No relevant docs found for: {query}"