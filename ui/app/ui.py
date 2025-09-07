import os
import gradio as gr
import httpx
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv("API_URL", "http://localhost:8000")

async def chat_fn(session_identifier: str, message: str, history: list[tuple[str, str]]):
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{API_URL}/chat",
            json={"session_id": session_identifier, "message": message},
        )
        resp.raise_for_status()
        data = resp.json()
        return data["reply"]

async def chat_wrapper(message, history):
    print("Message:", message)
    print("History:", history)
    return await chat_fn(session_id.value, message, history)

with gr.Blocks(title="CustomerServiceandConversationalAI") as demo:
    gr.Markdown("# CustomerServiceandConversationalAI")
    with gr.Row():
        session_id = gr.Textbox(label="Session ID", value="demo-session")
    chat = gr.ChatInterface(
        fn=chat_wrapper,
        title="Assistant",
        textbox=gr.Textbox(placeholder="Ask something..."),
    )

if __name__ == "__main__":
    demo.queue().launch(server_name="0.0.0.0", server_port=7860)