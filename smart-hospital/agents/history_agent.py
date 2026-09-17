"""
Patient History Agent for Smart Hospital.
Retrieves authorized patient historical medical records, allergy data, and past visits.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from google.adk.agents import Agent
from tools.hospital_tools import search_patient_records, get_appointment_history

history_agent = Agent(
    model="gemini-2.0-flash",
    name="history_agent",
    description="Retrieves historical medical records, allergy profiles, and past appointment history for authorized patients.",
    instruction="""
    You are the Patient History Agent for Smart Hospital.
    Your responsibilities:
    1. Retrieve patient health profile and allergy data using search_patient_records.
    2. Retrieve past appointment timeline using get_appointment_history.
    3. Provide accurate operational timelines of past visits and known allergies.
    
    Ensure patient authorization is verified before returning sensitive historical data.
    """,
    tools=[search_patient_records, get_appointment_history]
)
