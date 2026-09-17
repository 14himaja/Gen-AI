"""
Parallel Workflow Engine for Smart Hospital.
Demonstrates Google ADK Concept #4: Parallel Workflow (ParallelAgent).
Simultaneously gathers information from History Agent, Document Agent, and Appointment Agent.
"""
import sys
import os
import concurrent.futures
from typing import Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from google.adk.agents import Agent, ParallelAgent
from tools.hospital_tools import search_patient_records, read_document, get_appointment_history

# Instantiate dedicated sub-agent instances for ParallelAgent
par_history_agent = Agent(
    model="gemini-2.0-flash",
    name="par_history_agent",
    description="Gathers history concurrently.",
    instruction="Fetch patient history.",
    tools=[search_patient_records]
)

par_document_agent = Agent(
    model="gemini-2.0-flash",
    name="par_document_agent",
    description="Gathers document content concurrently.",
    instruction="Read medical document.",
    tools=[read_document]
)

par_appointment_agent = Agent(
    model="gemini-2.0-flash",
    name="par_appointment_agent",
    description="Gathers appointment info concurrently.",
    instruction="Fetch appointment timeline.",
    tools=[get_appointment_history]
)

parallel_visit_prep_agent = ParallelAgent(
    name="visit_preparation_parallel_gatherer",
    sub_agents=[
        par_history_agent,
        par_document_agent,
        par_appointment_agent
    ]
)

def run_parallel_workflow(patient_id: str = "PAT-1001", doc_id: str = "DOC-FILE-1") -> Dict[str, Any]:
    """
    Executes tasks in parallel using thread pool to demonstrate concurrent agent gathering:
    - Thread 1: History Agent fetches patient history & allergies.
    - Thread 2: Document Agent reads uploaded medical document.
    - Thread 3: Appointment Agent fetches upcoming/past appointments.
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_history = executor.submit(search_patient_records, patient_id)
        future_doc = executor.submit(read_document, doc_id, patient_id)
        future_appointments = executor.submit(get_appointment_history, patient_id)

        history_res = future_history.result()
        doc_res = future_doc.result()
        appointments_res = future_appointments.result()

    combined_summary = {
        "patient_id": patient_id,
        "patient_profile": history_res,
        "document_facts": doc_res,
        "appointments": appointments_res,
        "disclaimer": "⚠️ Combined parallel operational summary. Not a medical diagnosis."
    }

    return {
        "status": "completed",
        "workflow": "parallel",
        "parallel_execution_results": combined_summary
    }
