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
## 🧪 Running Automated Tests

The project includes a complete test suite built with `pytest` and `pytest-httpx` to validate the behavior of all MCP server tools. 

Since all HTTP requests are intercepted using Mocks, **you do not need to run the FastAPI server (Uvicorn) or the database in parallel to execute the tests.**

### 1. Ensure your Virtual Environment is active
In your terminal, make sure your `venv` is enabled:
```bash
# On Windows (PowerShell):
venv\Scripts\activate

# On Linux/macOS:
source venv/bin/activate

```

### 2. Run all tests

To execute the entire test suite simply, run the following command from the **root directory** of the project:

```bash
pytest

```

### 3. Check Code Coverage Report

To see the exact percentage of code paths tested and identify any line that wasn't executed, run the coverage analysis tool:

```bash
pytest --cov=mcp_server --cov-report term-missing testes/

```

> 💡 **Note on Coverage:** The report will show nearly 100% coverage. It is completely normal and expected for it to display **1 line as `Missing**` (specifically the final `mcp.run()` line). This happens because the actual MCP server instance is not initialized during automated test execution.

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

