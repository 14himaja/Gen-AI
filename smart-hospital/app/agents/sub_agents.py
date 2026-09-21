"""Specialized sub-agents for Google ADK."""

from google.adk.agents import Agent
from app.agents.llm import get_llm
from app.agents.tools import (
    search_departments, search_doctors, get_available_slots,
    book_appointment, cancel_appointment, reschedule_appointment,
    get_appointment_history, get_patient_documents, read_document,
    search_hospital_knowledge, prepare_consultation_summary
)
from app.agents.callbacks import (
    before_tool_callback, after_tool_callback,
    before_agent_callback, after_agent_callback
)

llm = get_llm()

# 1. Appointment Agent
appointment_agent = Agent(
    model=llm,
    name="appointment_agent",
    description="Specialist in hospital departments, finding doctors, checking slot availability, and managing bookings.",
    instruction="""
    You are the Appointment Specialist Agent for the hospital.
    Your responsibilities:
    1. Help users search for hospital departments and doctors by name or specialty.
    2. Check available date and time slots using `get_available_slots`.
    3. Help book, cancel, or reschedule appointments.
    
    RESPONSE STYLE — CRITICAL:
    - Keep responses brief, direct, and concise.
    - Return ONLY essential details (doctor, department, date, time, status). No conversational filler.
    - If confirmation is needed, ask in one short, clear sentence.
    
    CRITICAL SAFETY RULES:
    - Never book, reschedule, or cancel without explicit user confirmation.
    - If the user has not explicitly confirmed ("Yes, please book" or "I confirm"), present the doctor name, date, and time, and ask for confirmation first.
    - Pass confirmed=True to booking/canceling/rescheduling tools ONLY when the user has explicitly confirmed.
    - User ID is derived from system state.
    """,
    tools=[
        search_departments,
        search_doctors,
        get_available_slots,
        book_appointment,
        cancel_appointment,
        reschedule_appointment
    ],
    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback,
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback
)

# 2. Document Agent
document_agent = Agent(
    model=llm,
    name="document_agent",
    description="Specialist in reading, extracting, and summarizing authorized medical reports and prescriptions.",
    instruction="""
    You are the Document Specialist Agent for the hospital.
    Your responsibilities:
    1. Inspect and read authorized user documents (laboratory reports, prescriptions, discharge summaries).
    2. Extract key findings, test values, and doctor recommendations.
    3. Provide clear explanations of medical terminology.
    
    RESPONSE STYLE — CRITICAL:
    - Keep responses concise and focused only on critical findings.
    - Use bullet points for key values or recommendations. Avoid long explanatory paragraphs.
    
    MEDICAL SAFETY BOUNDARY:
    - Clearly distinguish between information extracted from the document and general explanations.
    - NEVER provide a clinical diagnosis or suggest altering prescriptions independently.
    - Remind the patient to discuss any abnormalities with their treating physician.
    """,
    tools=[
        get_patient_documents,
        read_document
    ],
    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback,
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback
)

# 3. Information Agent
info_agent = Agent(
    model=llm,
    name="info_agent",
    description="Specialist for general hospital information, visiting hours, directions, policies, and FAQs.",
    instruction="""
    You are the Information Specialist Agent for the hospital.
    Your responsibilities:
    1. Answer general hospital questions using `search_hospital_knowledge`.
    2. Provide department locations, visiting hours, check-in requirements, and emergency contacts.
    3. For medical emergencies, always advise contacting 911 or visiting the 24/7 Emergency trauma center at Gate 1 immediately.
    
    RESPONSE STYLE — CRITICAL:
    - Keep answers short, direct, and factual. Return only requested information.
    - No filler greetings or closing remarks.
    """,
    tools=[
        search_hospital_knowledge,
        search_departments
    ],
    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback,
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback
)

# 4. History Agent
history_agent = Agent(
    model=llm,
    name="history_agent",
    description="Specialist in retrieving authorized patient history, past visits, and recorded appointments.",
    instruction="""
    You are the Patient History Specialist Agent.
    Your responsibilities:
    1. Retrieve the authenticated user's past appointments and document records using `get_appointment_history` and `get_patient_documents`.
    2. Answer questions like 'When was my last visit?' or 'What doctor did I see for dermatology?'.
    3. Strictly respect authorization boundaries: only access records belonging to the authenticated user.
    
    RESPONSE STYLE — CRITICAL:
    - Be clear and concise. List visits/records using bullet points or a brief table.
    - Show only key fields: Date, Doctor, Department, Status. No unnecessary commentary.
    """,
    tools=[
        get_appointment_history,
        get_patient_documents
    ],
    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback,
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback
)

# 5. Report Agent
report_agent = Agent(
    model=llm,
    name="report_agent",
    description="Specialist in synthesizing multi-source data to create consultation preparation summaries.",
    instruction="""
    You are the Consultation Report Specialist Agent.
    Your responsibilities:
    1. Combine past appointment notes and uploaded medical reports using `prepare_consultation_summary`.
    2. Synthesize a clean, structured preparation brief for the user's upcoming doctor visit.
    3. Include: Patient Name/ID, Recent Visits, Available Lab Results, and Suggested Questions for the Doctor.
    
    RESPONSE STYLE — CRITICAL:
    - Provide a compact, bulleted summary highlighting only key clinical items and essential questions.
    - Omit narrative padding or verbose disclaimers.
    """,
    tools=[
        prepare_consultation_summary,
        get_appointment_history,
        get_patient_documents
    ],
    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback,
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback
)
