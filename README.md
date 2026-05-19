# Deep-Dish Reservation Bot 🍕

Deep-Dish is a backend service and MCP (Model Context Protocol) server designed to power an AI-driven WhatsApp chatbot for restaurant reservations. It bridges a reasoning AI engine with a lightweight, fast Python backend to manage users and bookings.

## 🏗 Architecture

This project is built using a two-tier architecture:

1. **FastAPI Backend:** A high-performance REST API that acts as the source of truth, managing an in-memory runtime database for users and reservations.
2. **FastMCP Server:** An integration layer that exposes the FastAPI endpoints as discrete tools. Any MCP-compatible AI agent (like Claude, LangChain, or LlamaIndex) can securely call these tools to perform actions on behalf of the user.

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

## 💻 Running the Application

To run the full stack locally, you need to spin up both the FastAPI backend and the MCP Server in two separate terminal windows.

### Step 1: Start the FastAPI Backend

This service must be running first so the MCP tools have an API to communicate with.

Open **Terminal 1** and run:

```bash
cd deep-dish-server
uvicorn app.main:app --reload
```

* The backend will be available at: `[http://127.0.0.1:8000](http://127.0.0.1:8000)`
* You can view the interactive API documentation at: `[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)`

### Step 2: Start the FastMCP Server

Once the backend is live, start the MCP server to expose the tools to your AI agent.

Open **Terminal 2** and run:

```bash
cd deep-dish-server
fastmcp run mcp_server.py -t http -p 3755
```

The mcp server is available at http://127.0.0.1:3755/mcp
