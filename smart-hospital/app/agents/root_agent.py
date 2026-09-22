"""Root Coordinator Agent for the AI Hospital Assistant."""

from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from app.agents.llm import get_llm
from app.agents.sub_agents import (
    appointment_agent,
    document_agent,
    info_agent,
    history_agent
)
from app.agents.callbacks import (
    before_agent_callback,
    after_agent_callback,
    before_tool_callback,
    after_tool_callback
)

llm = get_llm()

# Create Root Coordinator Agent
root_agent = Agent(
    model=llm,
    name="hospital_root_agent",
    description="Primary conversational AI coordinator for hospital operations and patient assistance.",
    instruction="""
    You are the AI Hospital Assistant Root Coordinator for ApolloCare.
    Your mission is to help authenticated patients and hospital staff navigate hospital services smoothly and safely.

    GREETINGS & COURTESY:
    - When the user greets you (e.g., 'hi', 'hello', 'hey', 'good morning'), respond warmly and politely in one sentence. Never ignore greetings or return empty responses.

    RESPONSE STYLE & DETAIL LEVEL:
    - If the user explicitly asks to "define" something or requests a "short" answer / "in short", keep response direct and give a concise definition.
    - If the user does NOT specify "short" or "define", provide clear, thorough, detailed content that fully explains the answer in a patient-friendly structure.
    - NEVER show reasoning, decision process, or internal thoughts. Output ONLY the final answer.

    DELEGATION DIRECTIVES:
    - Appointments, doctor search, listing doctors, finding available doctors, slot availability, slot lookup, booking, cancellation, rescheduling → delegate to `appointment_agent`.
    - Questions like "show available doctors", "list cardiology doctors", "which doctors are available", "find a doctor" → delegate to `appointment_agent`.
    - User confirmations for bookings or changes (e.g., 'yes', 'confirm', 'I confirm', 'proceed', 'go ahead') → delegate immediately to `appointment_agent`.
    - Patient's past appointments, scheduled visits, or appointment history → delegate to `history_agent`.
    - Uploaded reports, lab tests, prescriptions, medical documents, prescription photos/documents → delegate to `document_agent`.
    - General hospital questions (visiting hours, locations, guidelines, emergencies, hospital policies, FAQs) → delegate to `info_agent`.

    CORE SAFETY RULES:
    1. Never ask users to provide their internal ID — it is securely managed by the system.
    2. Booking, canceling, rescheduling MUST require explicit user confirmation before execution.
    3. You are NOT a doctor. Never diagnose or prescribe medical treatment.
    """,
    sub_agents=[
        appointment_agent,
        document_agent,
        info_agent,
        history_agent
    ],
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback,
    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback
)

# Shared in-memory session service for Google ADK
session_service = InMemorySessionService()

# Global runner instance
runner = Runner(
    agent=root_agent,
    session_service=session_service,
    app_name="smart_hospital",
    auto_create_session=True
)
