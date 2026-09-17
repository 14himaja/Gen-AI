"""
Document Agent for Smart Hospital.
Processes uploaded prescriptions, lab reports, and discharge summaries.
Strictly distinguishes extracted facts from interpretations and outputs structured Pydantic DocumentSummary.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from google.adk.agents import Agent
from tools.hospital_tools import read_document
from schemas.models import DocumentSummary

document_agent = Agent(
    model="gemini-2.0-flash",
    name="document_agent",
    description="Processes uploaded medical documents (prescriptions, lab reports, discharge summaries) and extracts structured facts.",
    instruction="""
    You are the Document Agent for Smart Hospital.
    Your responsibilities:
    1. Read uploaded medical documents using read_document.
    2. Extract objective facts (medicine names, dosage, test numbers, allergy warnings).
    3. Clearly distinguish extracted factual statements from interpretations.
    4. Provide warnings if document image quality is low or key information is unreadable.
    
    ⚠️ Mandatory Rule: Include non-diagnosis disclaimer in all outputs. Never diagnose diseases.
    """,
    tools=[read_document],
    output_schema=DocumentSummary,
    output_key="document_summary"
)
