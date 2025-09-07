# Customer Service and Conversational AI

This project provides a conversational AI system that combines **FastAPI** and **LangGraph agents** for backend logic with a **Gradio UI** for interaction. 
It allows running and testing customer service–style AI agents locally or inside Docker.

---

## 📂 Project Structure

![Screenshot 2025-09-07 at 8.54.40 AM.png](../../../../../../var/folders/k2/2clb9kjd3d9d51qjmf4gx83c0000gn/T/TemporaryItems/NSIRD_screencaptureui_zKcQsK/Screenshot%202025-09-07%20at%208.54.40%E2%80%AFAM.png)


- **Backend (FastAPI + LangGraph agents):**
  - Runs at: `http://0.0.0.0:8000`

- **Frontend (Gradio app):**
  - Runs at: `http://0.0.0.0:7860`

---

## ⚙️ Prerequisites

Before running the application, ensure the following:

1. **`.env` file**
   - Must exist in the root of the repository (same level as `README.md`).
   - See the [Sample `.env` file](#sample-env-file) below for a template.

2. **[Ollama](https://ollama.ai/) installed**
   - Required to run LLaMA models locally.
   - Ensure the model defined in your `.env` (`OLLAMA_MODEL`) is already available.

   Example:
   ```bash
   ollama pull llama3.2:latest
3. Docker
   - Ensure Docker is installed and running.

## Quickstart
# Clone the repository
 - git clone https://github.com/JenishGnanasicamani/CustomerServiceandConversationalAI-.git
 - cd CustomerServiceandConversationalAI

# Create your .env file sample below and adjust values
# Build and run containers
docker-compose up --build

PROJECT_NAME=CustomerServiceandConversationalAI
ENVIRONMENT=development

API_HOST=0.0.0.0
API_PORT=8000

# For the UI container talking to API via Docker network
INTERNAL_API_URL=http://api:8000
# For local debugging outside Docker
EXTERNAL_API_URL=http://localhost:8000

# === Ollama ===
# Host-installed Ollama
OLLAMA_BASE_URL=http://host.docker.internal:11434
# Choose a model present/compatible with your Ollama install
OLLAMA_MODEL=llama3.2:latest

# === MongoDB Atlas ===
# Format: mongodb+srv://<user>:<pass>@<cluster>/dbname?retryWrites=true&w=majority
MONGODB_URI=mongodb+srv://cia_db_user:<passwd>@capstone-project.yyfpvqh.mongodb.net/?retryWrites=true&w=majority&appName=CAPSTONE-PROJECT
MONGODB_DB=csai
MONGODB_COLLECTION=messages

# === CORS ===
ALLOWED_ORIGINS=*
