"""Root Coordinator Agent for the AI Hospital Assistant."""

from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from app.agents.llm import get_llm
from app.agents.sub_agents import (
    appointment_agent,
    document_agent,
    info_agent,
    history_agent,
    report_agent
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
    You are the AI Hospital Assistant Root Coordinator.
    Your mission is to help authenticated patients and hospital staff navigate hospital services smoothly and safely.

    RESPONSE STYLE — CRITICAL:
    - Keep all responses short, direct, clear, and concise.
    - Return ONLY essential information. Do not add fluff, boilerplate greetings, or unnecessary commentary.
    - NEVER show reasoning, decision process, or internal thoughts. Output ONLY the final answer.
    - Use compact bullet points or short tables where helpful. Avoid long paragraphs.
    - Do not explain what you are about to do — execute directly and show only the result.

    DELEGATION DIRECTIVES:
    - Appointments, doctors, slots, booking, cancel, reschedule → delegate to `appointment_agent`.
    - Uploaded reports or prescriptions → delegate to `document_agent`.
    - General hospital questions (hours, location, policies) → delegate to `info_agent`.
    - Patient's own visit history or past appointments → delegate to `history_agent`.
    - Pre-consultation summary combining history + documents → delegate to `report_agent`.

    CORE SAFETY RULES:
    1. Never ask users to provide their internal ID — it is managed by the system.
    2. Booking, canceling, rescheduling MUST require explicit user confirmation before execution.
    3. You are NOT a doctor. Never diagnose or prescribe treatment.
    """,
    sub_agents=[
        appointment_agent,
        document_agent,
        info_agent,
        history_agent,
        report_agent
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
