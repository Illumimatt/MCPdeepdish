# Deep-Dish Reservation Bot 🍕

Deep-Dish is a backend service and MCP (Model Context Protocol) server designed to power an AI-driven WhatsApp chatbot for restaurant reservations. It bridges a reasoning AI engine with a lightweight, fast Python backend to manage users and bookings.

## 🏗 Architecture

This project is built using a three-tier architecture:

1. **FastAPI Backend:** A high-performance REST API that acts as the source of truth, managing an in-memory runtime database for users and reservations.
2. **FastMCP Server:** An integration layer that exposes the FastAPI endpoints as discrete MCP tools over SSE (Server-Sent Events). Any MCP-compatible AI agent can securely call these tools to perform actions on behalf of the user.
3. **Telegram Bot:** The user-facing entry point. It receives messages, sends them to Ollama for reasoning, and forwards any tool calls to the MCP server. The bot maintains a persistent SSE connection to avoid per-message reconnection overhead.

---

## 📋 Prerequisites

* Python 3.8+
* `pip` (Python package installer)

---

## 🚀 Installation & Setup

**1. Clone the repository and navigate to the project directory:**

```bash
git clone <your-repo-url>
cd deep-dish

```

**2. Create a virtual environment (Recommended):**

```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

```

**3. Install dependencies:**

```bash
pip install -r requirements.txt

```
---
## 🧪 Running Automated Tests

The project includes a robust test suite built with `pytest` to validate the behavior of all MCP server tools. The suite is split into two categories: **Mock Tests** (isolated) and **Integration Tests** (real API).

### 1. Ensure your Virtual Environment is active
In your terminal, make sure your `venv` is enabled:

```bash
# On Windows (PowerShell):
venv\Scripts\Activate

# On Linux/macOS:
source venv/bin/activate

```

### 2. Run Mock Tests (Isolated)

These tests intercept all HTTP requests using Mocks. **You do not need to run the FastAPI server (Uvicorn) or the database to execute them.**

To run the mock suite and check the code coverage, execute from the root directory:

```bash
pytest --cov=mcp_server --cov-report term-missing testes/

```

> 💡 *Note on Coverage: It is expected to display 1 line as `Missing` (specifically the final `mcp.run()` line), since the actual MCP server instance is not initialized during mock execution.*

### 3. Run Integration Tests (Real API)

These tests hit the live endpoints to ensure the MCP server and the FastAPI backend work perfectly together. They validate the complete lifecycle of both **Users** and **Reservations**. They use dynamic data generation, meaning they will not clash with existing database records.

To run them, **make sure your FastAPI server is running (`uvicorn main:app --reload`)** in a separate terminal, then run:

```bash
pytest -m integration
```
---

## 💻 Running the Application

To run the full stack locally, you need to start three services in order. Make sure your virtual environment is activated (`source venv/bin/activate`) in all terminals.

### Step 1: Start the FastAPI Backend (Terminal 1)

This must run first — the MCP server depends on it.

```bash
cd deep-dish-server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

* Backend available at: `http://127.0.0.1:8000`
* Interactive API docs: `http://127.0.0.1:8000/docs`

### Step 2: Start the FastMCP Server (Terminal 2)

The MCP server bridges the Telegram bot to the FastAPI backend. It exposes tools over SSE.

```bash
cd deep-dish-server
fastmcp run mcp_server.py -t sse --host 127.0.0.1 -p 3755
```

* MCP server available at: `http://127.0.0.1:3755/sse`

> **Note:** The `API_BASE_URL` environment variable must point to the FastAPI backend.
> The default is `http://127.0.0.1:8000`, so no extra config is needed for local development.

### Step 3: Start the Telegram Bot (Terminal 3)

The bot connects to the MCP server over a **persistent SSE connection** (reused across messages to avoid per-message overhead) and uses Ollama for LLM reasoning.

Make sure **Ollama is running** with your chosen model pulled (default: `qwen3.5:latest`):

```bash
ollama pull qwen3.5:latest
```

Then start the bot from the project root:

```bash
python telegram_bot.py
```

| Environment Variable | Default | Description |
|---|---|---|
| `TELEGRAM_TOKEN` | *(see code)* | Your Telegram Bot API token |
| `OLLAMA_MODEL` | `qwen3.5:latest` | Ollama model to use for reasoning |

---

## 🐳 Running with Docker

The repository now includes a Docker setup with two containers: one for the FastAPI backend and one for the MCP server.

From the repository root, run:

```bash
docker compose up --build
```

This exposes:

* FastAPI at `http://127.0.0.1:8000`
* MCP server at `http://127.0.0.1:3755/sse`

To run the test suite from the `testes` folder against the live stack, use:

```bash
docker compose run --rm tests
```

That command waits for the API healthcheck, mounts the repository, and runs `pytest /workspace/testes` inside the container.

If you want to run only one service, you can still use the same image and override the command in Docker Compose.
