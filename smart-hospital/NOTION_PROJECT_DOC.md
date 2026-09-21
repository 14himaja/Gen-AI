# 🏥 ApolloCare Smart Hospital AI Assistant — Project & Architecture Documentation

> **Project Overview**: ApolloCare is an enterprise-grade, conversational multi-agent healthcare operating assistant powered by **Google ADK (Agent Development Kit)**, **FastAPI**, **SQLite RAG**, and **LiteLLM**. It dynamically supports **any LLM Provider and API key** (OpenRouter, Gemini, Groq, Grok/xAI, OpenAI, Anthropic, DeepSeek, etc.) configured via environment variables without code changes.

---

## 📌 1. Problem Statement

Modern healthcare navigation is fragmented, inefficient, and stressful for candidates (patients) and hospital administrators alike:

- ⏳ **Long Phone Waiting Times**: Outpatients spend 15–30 minutes on phone holds just to check doctor availability or book/reschedule appointment slots.
- 📋 **Patient Medical Paperwork Overload**: Patients receive complex lab reports (e.g. Complete Blood Count, Serum IgE) filled with medical jargon that they cannot easily interpret before seeing a doctor.
- 📑 **Unprepared Doctor Consultations**: Doctors have limited 10–15 minute consultation windows, but patients often forget their past medical history or fail to summarize their recent test results.
- 🏥 **Outdated Hospital Knowledge Bases**: Hospital policies (visiting hours, ICU guidelines, emergency trauma rules) change frequently. Admins lack a simple tool to upload new guidelines that immediately inform AI assistants without expensive model fine-tuning.

---

## 💡 2. Solution: ApolloCare Smart Hospital AI

**ApolloCare** solves these challenges by combining **Multi-Agent Orchestration**, **Structured SQL Database Tool Execution**, **Semantic Document Chunking RAG**, and **Dynamic Multi-Provider LLM Integration**:

1. **Multi-Agent Orchestration (Google ADK)**: A coordinator agent (`root_agent`) routes queries to specialized sub-agents (`appointment_agent`, `document_agent`, `info_agent`, `history_agent`, `report_agent`).
2. **Safety Confirmation Guardrails**: Actionable operations (booking, canceling, rescheduling) require explicit user confirmation (`confirmed=True`) before mutating database records.
3. **Dynamic LLM Multi-Provider System**: Uses LiteLLM to accept any LLM provider & API key in `.env` (Gemini, OpenRouter, Groq, Grok, OpenAI, Anthropic) with zero code modifications.
4. **Admin Dashboard & RAG Chunking Engine**: Hospital Admins can upload policy documents. The backend automatically applies sliding-window text chunking (400 chars, 80 char overlap) and indexes chunks into the RAG vector search engine instantly.

---

## 🤖 3. Agents & Their Specialized Capabilities

```mermaid
graph TD
    Root["hospital_root_agent - Primary Coordinator"]
    
    Root --> Appt["appointment_agent - Doctors, Slots, Bookings"]
    Root --> Doc["document_agent - Lab Reports & Prescriptions"]
    Root --> Info["info_agent - Visiting Hours & FAQs"]
    Root --> Hist["history_agent - Patient Past Visits"]
    Root --> Rep["report_agent - Pre-Consultation Brief"]
```

| Agent Name | Primary Role & Responsibilities | Available Tools |
| :--- | :--- | :--- |
| **`hospital_root_agent`** | Primary conversational coordinator; greets candidates and routes intent to sub-agents. | Sub-agent delegation |
| **`appointment_agent`** | Specialist in department lookups, finding doctors, checking slot availability, and managing bookings with safety confirmation guardrails. | `search_departments`, `search_doctors`, `get_available_slots`, `book_appointment`, `cancel_appointment`, `reschedule_appointment` |
| **`document_agent`** | Inspects, extracts, and explains authorized medical lab reports, prescriptions, and test metrics safely. | `get_patient_documents`, `read_document` |
| **`info_agent`** | Answers general hospital questions, visiting hours, locations, and emergency directions. | `search_hospital_knowledge`, `search_departments` |
| **`history_agent`** | Retrieves past appointment records strictly isolated to the authenticated candidate. | `get_appointment_history`, `get_patient_documents` |
| **`report_agent`** | Synthesizes multi-source data (past visits + lab results) into a structured pre-consultation briefing sheet. | `prepare_consultation_summary` |

---

## 🔄 4. High-Level Activity Flow

```mermaid
flowchart TD
    Start(["Candidate Sends Message"]) --> AuthCheck{"Is Candidate Authenticated?"}
    AuthCheck -->|No| DemandAuth["Return HTTP 401 / Demand JWT Token"]
    AuthCheck -->|Yes| LLMRouter["LLM Intent Classification"]
    
    LLMRouter --> RouteChoice{"Select Sub-Agent & Action"}
    
    RouteChoice -->|Booking Action| CheckConfirm{"Is Action Confirmed by User?"}
    CheckConfirm -->|No| DemandConfirm["Return Confirmation Prompt"]
    CheckConfirm -->|Yes| ExecSQL["Execute SQL Mutation"]
    
    RouteChoice -->|Policy Question| RAGSearch["Search Knowledge Base & Admin Chunks"]
    RAGSearch --> InjectPrompt["Inject Retrieved Chunks into LLM Prompt"]
    InjectPrompt --> LLMGen["LLM Synthesizes Grounded Answer"]
    
    RouteChoice -->|Lab Analysis| ReadDoc["Read Patient Medical Document"]
    ReadDoc --> ExplainLLM["LLM Explains Findings with Medical Disclaimer"]
    
    ExecSQL --> Respond["Return Clean Result to Candidate"]
    LLMGen --> Respond
    ExplainLLM --> Respond
    DemandConfirm --> Respond
```

---

## 📜 5. Sequence Diagrams

### 5.1 Candidate Sequence Diagram (Appointment Booking & Lab Explanation)

```mermaid
sequenceDiagram
    autonumber
    actor Candidate as Candidate (Patient)
    participant UI as Web App (Frontend)
    participant API as FastAPI Backend
    participant ADK as Google ADK Root Agent
    participant Agent as appointment_agent / document_agent
    participant DB as SQLite Database / RAG

    Candidate->>UI: Type "Book appointment with Dr. Sharma tomorrow at 10:00 AM"
    UI->>API: POST /api/chat { message, JWT token }
    API->>ADK: Pass query to Root Agent
    ADK->>Agent: Route to appointment_agent
    Agent->>DB: Check slot availability (get_available_slots)
    DB-->>Agent: Slot AVAILABLE
    Agent-->>ADK: Return "Please confirm: Book Dr. Sharma on 2026-09-22 at 10:00 AM?"
    ADK-->>API: Response (confirmation_required)
    API-->>UI: Display confirmation prompt
    
    Candidate->>UI: Type "Yes, I confirm the booking"
    UI->>API: POST /api/chat { message, confirmed=True }
    API->>ADK: Pass confirmation
    ADK->>Agent: Route to appointment_agent
    Agent->>DB: Execute book_appointment (INSERT INTO appointments)
    DB-->>Agent: Appointment APPT-1001 created
    Agent-->>ADK: Success response
    ADK-->>API: Return final booking confirmation
    API-->>UI: Display appointment booked card
```

---

### 5.2 Admin Sequence Diagram (Document Upload & Semantic Chunking)

```mermaid
sequenceDiagram
    autonumber
    actor Admin as Hospital Administrator
    participant UI as Admin Dashboard UI
    participant API as Admin API (/api/admin/documents)
    participant Chunker as Chunking Engine (chunk_text)
    participant DB as SQLite DB (hospital_doc_chunks)
    actor Candidate as Candidate Query

    Admin->>UI: Paste new "Pediatric ICU Visitor Guidelines"
    UI->>API: POST /api/admin/documents { title, category, content }
    API->>Chunker: Pass content (chunk_size=400, overlap=80)
    Chunker-->>API: Returns 4 overlapping text chunks
    API->>DB: INSERT INTO hospital_documents & hospital_doc_chunks
    DB-->>API: Document & Chunks saved
    API-->>UI: Success response (4 chunks generated)
    
    Note over Candidate, DB: Later, Candidate asks: "What are ICU visiting rules?"
    Candidate->>API: POST /api/chat "What are ICU visiting rules?"
    API->>DB: search_knowledge_base("ICU visiting rules")
    DB-->>API: Returns matching Chunk #2 ("PICU visiting hours 5-6 PM...")
    API-->>Candidate: LLM answers grounded strictly on retrieved chunk!
```

---

## 🤝 6. Agent Communication & Workflow Architecture

Google ADK supports complex multi-agent workflows built into ApolloCare:

```mermaid
graph LR
    subgraph SequentialWorkflow ["1. Sequential Document Processing Pipeline"]
        E["Document Extractor Agent"] --> V["Metric Validator Agent"] --> S["Patient Summary Synthesizer Agent"]
    end

    subgraph ParallelWorkflow ["2. Parallel Multi-Source Gathering"]
        H["Parallel History Fetcher"] --> C["Final Brief Compiler Agent"]
        D["Parallel Document Fetcher"] --> C
    end

    subgraph LoopWorkflow ["3. Iterative Quality Refinement Loop"]
        DG["Draft Summary Generator"] <--> SR["Medical Safety Reviewer (Max 2 Iterations)"]
    end
```

---

## 🏛️ 7. Complete System Architecture Diagram

```mermaid
graph TB
    subgraph ClientLayer ["Client Layer"]
        WebUI["Web App UI (Vanilla HTML5 / CSS3 / JS)"]
        AdminUI["Admin Dashboard & Chunk Inspector"]
    end

    subgraph APIGatewayLayer ["API Gateway Layer (FastAPI)"]
        AuthAPI["/api/auth (JWT, Registration, OTP)"]
        HospAPI["/api/hospital (Departments, Doctors, Slots)"]
        ChatAPI["/api/chat (Multi-Turn Chat Endpoint)"]
        AdminAPI["/api/admin (Doc Upload, Chunk Stats)"]
    end

    subgraph ADKLayer ["Agentic Intelligence Layer (Google ADK)"]
        RootAgent["hospital_root_agent"]
        SubAgents["Specialized Sub-Agents (Appt, Doc, Info, History, Report)"]
        LiteLLMWrapper["LiteLLM Provider Adapter"]
    end

    subgraph LLMLayer ["LLM Model Provider Layer"]
        Gemini["Google Gemini API"]
        OpenRouter["OpenRouter API"]
        Groq["Groq Router"]
        Grok["Grok / xAI"]
        OpenAI["OpenAI API"]
    end

    subgraph DataLayer ["Data & Storage Layer"]
        SQLite["SQLite Database (hospital.db)"]
        Tables["Tables: users, appointments, slots, doctors, documents, knowledge_base, hospital_doc_chunks"]
        ChunkEngine["Semantic Text Chunker (app/services/chunker.py)"]
    end

    WebUI --> AuthAPI
    WebUI --> HospAPI
    WebUI --> ChatAPI
    AdminUI --> AdminAPI
    
    ChatAPI --> RootAgent
    AdminAPI --> ChunkEngine
    ChunkEngine --> SQLite
    
    RootAgent --> SubAgents
    SubAgents --> LiteLLMWrapper
    
    LiteLLMWrapper --> Gemini
    LiteLLMWrapper --> OpenRouter
    LiteLLMWrapper --> Groq
    LiteLLMWrapper --> Grok
    LiteLLMWrapper --> OpenAI
    SubAgents --> SQLite
```

---

## 🔬 8. LLM vs RAG vs Tool Execution Matrix

| Feature | LLM Used | RAG Used | Tool / API Used | Database Used | Reason & Architectural Purpose |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Candidate Login & Registration** | ❌ | ❌ | ✅ | ✅ | Deterministic authentication, passlib bcrypt password verification, JWT generation. |
| **OTP Verification** | ❌ | ❌ | ✅ | ✅ | Deterministic OTP state check. |
| **Doctor & Department Search** | Optional | ❌ | ✅ | ✅ | Retrieves parameterized doctor catalog from SQL database. |
| **Slot Availability Search** | Optional | ❌ | ✅ | ✅ | Queries open slots for selected doctor & date. |
| **Appointment Booking / Cancel / Reschedule** | Optional | ❌ | ✅ | ✅ | Executes state mutation on database after user confirmation (`confirmed=True`). |
| **Patient Appointment History** | Optional | ❌ | ✅ | ✅ | Fetches isolated past visit ledger for authenticated user. |
| **Hospital General FAQ** | ✅ | Maybe | ❌ | ❌ | Answers general queries using LLM or seed knowledge base. |
| **Hospital Policy & Guidelines Question** | ✅ | ✅ | ❌ | ✅ | Retrieves admin-uploaded text chunks via RAG and synthesizes grounded answer. |
| **Document Explanation & Lab Analysis** | ✅ | Optional | ✅ | ✅ | Reads patient's authorized lab PDF/text and explains values with medical disclaimer. |
| **Pre-Consultation Summary Brief** | ✅ | Optional | ✅ | ✅ | Synthesizes multi-source data (appointments + lab reports) via `report_agent`. |
| **User Authorization (RBAC)** | ❌ | ❌ | ✅ | ✅ | Enforces JWT sub validation & patient data isolation deterministically. |
| **Admin Document Upload & Chunking** | ❌ | ✅ | ✅ | ✅ | Applies sliding window text chunking (400 chars, 80 overlap) & stores chunks. |

---

## 🔒 9. Security, Authorization & Data Isolation

1. **Strict User Isolation**: Patients can ONLY view their own records (`P1001` cannot read `P1002` appointments or documents).
2. **Role-Based Access Control (RBAC)**: Admin endpoints (`/api/admin/*`) enforce `require_admin` dependency and reject patient tokens with HTTP 403 Forbidden.
3. **No Arbitrary SQL Generation**: Agents call parameterized Python tool functions (`get_appointment_history`, `book_appointment`), preventing SQL injection risks.
4. **Safety Confirmation Guardrails**: Actionable database mutations require two-turn confirmation (`confirmed=True`) before execution.
5. **Audit Logging**: Every executed tool action is recorded with timestamp, user_id, tool_name, parameters, and status in SQLite `audit_logs`.

---

## 🔮 10. Future Work: Real-Time Voice Agent Integration

The next evolution of ApolloCare will integrate a **Real-Time Voice Agent** powered by the **Gemini Live API** (Multimodal WebSockets):

> **Gemini Live API Architecture**:
> - **Bi-Directional WebSockets**: Continuous low-latency audio streaming (<300ms response time).
> - **Native Voice-to-Voice**: Eliminates traditional Speech-to-Text (STT) and Text-to-Speech (TTS) pipeline friction.
> - **Function Calling over Voice**: Candidates can speak naturally ("Book an appointment with Dr. Sharma tomorrow"), while Gemini Live triggers ADK tool calls directly over the audio socket!

```mermaid
sequenceDiagram
    autonumber
    actor Candidate as Candidate (Voice)
    participant Mic as Browser Audio Stream
    participant WS as WebSocket Server (FastAPI)
    participant LiveAPI as Gemini Live API (Multimodal Voice)
    participant Tools as ADK Tool Functions (SQLite)

    Candidate->>Mic: Speaks "Is Dr. Sharma available tomorrow morning?"
    Mic->>WS: Stream PCM 16kHz Audio Chunks over WebSocket
    WS->>LiveAPI: Bi-directional Audio Stream
    LiveAPI->>Tools: Trigger Function Call get_available_slots(doctor_id='DOC-001')
    Tools-->>LiveAPI: Return available slots JSON
    LiveAPI-->>WS: Stream Synthesized Natural Voice Response
    WS-->>Mic: Play Audio Stream
    Mic-->>Candidate: "Dr. Sharma is available at 10:00 AM and 11:30 AM tomorrow."
```

---

### Summary Checklist

- [x] Problem Statement & Solution
- [x] List of Agents & Capabilities
- [x] High-Level Activity Diagram
- [x] Sequence Diagrams (Candidate & Admin)
- [x] Multi-Agent Communication Diagram
- [x] Complete Visual System Architecture Diagram (Notion-Compatible Syntax)
- [x] RAG Architecture & Sliding-Window Chunking (400/80)
- [x] LLM vs RAG vs Tool Execution Matrix
- [x] Security, RBAC & Isolation Documentation
- [x] Future Work (Gemini Live API Voice Agent Integration)

