FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8000
# Wait for host-installed Ollama and the required model before starting API
CMD sh -c ' \
  OLLAMA_URL="${OLLAMA_BASE_URL:-http://host.docker.internal:11434}"; \
  MODEL="${OLLAMA_MODEL:-llama3.1}"; \
  echo "Waiting for Ollama at $OLLAMA_URL ..."; \
  until curl -fsS "$OLLAMA_URL/api/tags" > /dev/null; do \
    echo "Ollama not reachable yet, retrying..."; sleep 2; \
  done; \
  echo "Ollama reachable. Checking for model: $MODEL ..."; \
  until curl -fsS "$OLLAMA_URL/api/tags" | grep -q "\"name\":\"$MODEL\""; do \
    echo "Model $MODEL not found yet on host Ollama. Please pull it on the host (outside Docker). Retrying..."; sleep 3; \
  done; \
  echo "Model $MODEL is present. Starting API..."; \
  uvicorn app.main:app --host 0.0.0.0 --port 8000 \
'