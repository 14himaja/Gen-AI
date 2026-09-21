# 🏥 Smart Hospital AI Assistant

A conversational, multi-agent AI healthcare operations assistant built with **Google ADK**, **FastAPI**, **Pydantic v2**, and **FastMCP**, configured to run seamlessly with the **Groq API** and `openai/gpt-oss-120b`.

---

## 🌟 Key Capabilities (PRD Implementation)

1. **Authentication & Identity Verification (FR-001 - FR-006)**:
   - User registration and OTP simulation.
   - JWT session management with role-based access (Patient, Doctor, Staff, Admin).
   - "LLM is never the security boundary" – identity context is injected into ADK session state directly from validated tokens.

2. **Hospital Operations & Catalog (FR-007 - FR-013)**:
   - Department and doctor directory search.
   - Real-time slot availability checking.
   - Booking, cancellation, and rescheduling workflows with **action confirmation guardrails**.

3. **Medical Document Processing (FR-014 - FR-016)**:
   - Parsing and summarizing laboratory reports and prescriptions.
   - Medical safety boundaries preventing unauthorized autonomous diagnoses.

4. **Hospital Knowledge Base & RAG (FR-017, FR-023)**:
   - Fast retrieval of hospital policies, visiting hours, check-in instructions, and emergency guidelines.

5. **Multi-Agent Architecture with Google ADK (FR-024)**:
   - **`hospital_root_agent`**: Main coordinator and intent router.
   - **`appointment_agent`**: Doctor search, slots, and booking.
   - **`document_agent`**: Report extraction and plain-English translation.
   - **`info_agent`**: Hospital FAQs, visiting hours, and policies.
   - **`history_agent`**: Strictly authorized patient history.
   - **`report_agent`**: Pre-consultation briefing synthesis.

6. **Agent Workflow Patterns (PRD Section 27)**:
   - **Sequential Workflow** (`SequentialAgent`): Document extraction $\rightarrow$ reference range validation $\rightarrow$ summary synthesis.
   - **Parallel Workflow** (`ParallelAgent`): Concurrent fetch of past history + documents $\rightarrow$ consultation brief compiler.
   - **Loop Workflow** (`LoopAgent`): Iterative draft generation and safety policy review.

7. **Standard Model Context Protocol (MCP) Server (FR-021)**:
   - FastMCP service in `app/mcp_server/server.py` exposing hospital capabilities.

---

## 🚀 Quick Start

### 1. Configure Environment
Ensure your `.env` in the `smart-hospital/` directory contains:
```ini
GROK_API_KEY="gsk_..."
MODEL="openai/gpt-oss-120b"
```

### 2. Run the FastAPI REST Server
```bash
python run.py serve
```
Interactive OpenAPI documentation will be accessible at:
👉 **`http://127.0.0.1:8000/docs`**

### 3. Run the Interactive CLI Chat Session
Chat with the Google ADK multi-agent assistant directly from your terminal as patient Rahul (`P1001`):
```bash
python run.py chat --user P1001
```

### 4. Run the Automated Tests
```bash
python run.py test
# or
pytest tests/ -v
```

---

## 📂 Project Structure

```text
smart-hospital/
├── app/
│   ├── __init__.py
│   ├── config.py             # Settings, environment, and model configuration
│   ├── models.py             # Pydantic v2 domain schemas (Users, Doctors, Appointments, Docs)
│   ├── database.py           # In-memory database with pre-seeded synthetic data
│   ├── main.py               # FastAPI application factory and lifespan
│   ├── api/                  # REST API routers
│   │   ├── auth.py           # Registration, OTP verification, JWT login
│   │   ├── hospital.py       # Mock hospital REST API (/departments, /doctors, /slots, etc.)
│   │   └── chat.py           # Chat endpoint connecting to Google ADK Runner
│   ├── agents/               # Google ADK Multi-Agent System
│   │   ├── llm.py            # LiteLLM provider initialization for Groq
│   │   ├── tools.py          # Deterministic hospital function tools
│   │   ├── callbacks.py      # Authorization checks, confirmation guardrails, audit logging
│   │   ├── sub_agents.py     # Appointment, Document, Info, History, Report agents
│   │   ├── workflows.py      # SequentialAgent, ParallelAgent, LoopAgent workflows
│   │   └── root_agent.py     # Main Root Coordinator and Runner
│   └── mcp_server/           # Model Context Protocol (MCP) server
│       └── server.py         # FastMCP tools exposure
├── tests/
│   └── test_smart_hospital.py# Comprehensive automated test suite
├── run.py                    # Unified CLI runner (serve, chat, test)
├── requirements.txt
└── .env
```
