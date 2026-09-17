"""
Sequential Workflow Engine for Smart Hospital.
Demonstrates Google ADK Concept #3: Sequential Workflow (SequentialAgent).
Pipeline: Patient Records (History Agent) -> Document Parsing (Document Agent) -> Summary Generation (Report Agent).
"""
import sys
import os
from typing import Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from google.adk.agents import Agent, SequentialAgent
from tools.hospital_tools import (
    search_patient_records,
    read_document,
    create_summary
)

# Instantiate dedicated sub-agent instances for SequentialAgent pipeline
seq_history_agent = Agent(
    model="gemini-2.0-flash",
    name="seq_history_agent",
    description="Retrieves patient records for sequential pipeline.",
    instruction="Retrieve patient record using search_patient_records.",
    tools=[search_patient_records]
)

seq_document_agent = Agent(
    model="gemini-2.0-flash",
    name="seq_document_agent",
    description="Parses document for sequential pipeline.",
    instruction="Parse document using read_document.",
    tools=[read_document]
)

seq_report_agent = Agent(
    model="gemini-2.0-flash",
    name="seq_report_agent",
    description="Generates final visit report for sequential pipeline.",
    instruction="Format summary report using create_summary.",
    tools=[create_summary]
)

sequential_visit_summary_agent = SequentialAgent(
    name="doctor_summary_sequential_pipeline",
    sub_agents=[
        seq_history_agent,
        seq_document_agent,
        seq_report_agent
    ]
)

def run_sequential_workflow(patient_id: str = "PAT-1001", doc_id: str = "DOC-FILE-1") -> Dict[str, Any]:
    """
    Executes the sequential workflow pipeline programmatically:
    Step 1: History Agent retrieves patient records.
    Step 2: Document Agent parses uploaded document facts.
    Step 3: Report Agent aggregates facts into final visit summary.
    """
    history_record = search_patient_records(patient_id)
    doc_data = read_document(doc_id, patient_id)
    
    summary_text = (
        f"PATIENT VISIT SUMMARY\n"
        f"Patient ID: {patient_id} ({history_record.get('name', 'Patient')})\n"
        f"Allergies: {', '.join(history_record.get('allergies', []))}\n"
        f"Medical History: {'; '.join(history_record.get('medical_history_summary', []))}\n"
        f"Extracted Document ({doc_data.get('title', 'Doc')}): {doc_data.get('content', '')}\n"
        f"Disclaimer: ⚠️ Operational summary for doctor visits. Not a medical diagnosis."
    )
    
    save_res = create_summary(patient_id, summary_text)
    
    return {
        "status": "completed",
        "workflow": "sequential",
        "steps": [
            {"agent": "seq_history_agent", "output": history_record},
            {"agent": "seq_document_agent", "output": doc_data},
            {"agent": "seq_report_agent", "output": summary_text}
        ],
        "final_summary": save_res
    }
