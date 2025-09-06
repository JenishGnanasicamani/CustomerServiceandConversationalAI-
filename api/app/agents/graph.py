from typing import Any, Dict, List, TypedDict
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from ..config import settings

# Graph state is a dict with a growing transcript
State = Dict[str, Any]

system_prompt = (
    "You are a helpful, concise customer service assistant. "
    "Answer clearly. If you use a tool, summarize results back to the user."
)

# Create the Ollama-backed chat model
llm = ChatOllama(base_url=settings.OLLAMA_BASE_URL, model=settings.OLLAMA_MODEL)


async def node_llm(state: State) -> State:
    # Reconstruct message list; adapt if you decide to store richer history
    messages: List = [SystemMessage(content=system_prompt)]
    for m in state.get("history", []):
        if m.get("user"):
            messages.append(HumanMessage(content=m["user"]))
        if m.get("assistant"):
            # If you want to use AIMessage, you can, but HumanMessage suffices for simple replay
            messages.append(HumanMessage(content=m["assistant"]))
    messages.append(HumanMessage(content=state["input"]))

    resp = await llm.ainvoke(messages)
    return {"output": resp.content}



class GraphState(TypedDict, total=False):
    input: str
    output: str
    history: List[Dict[str, str]]

builder = StateGraph(GraphState)
builder.add_node("llm", node_llm)
builder.set_entry_point("llm")
builder.add_edge("llm", END)

app_graph = builder.compile()
