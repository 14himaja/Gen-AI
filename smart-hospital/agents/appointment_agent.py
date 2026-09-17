"""
Appointment Agent for Smart Hospital.
Handles doctor search, department queries, available slots, booking, cancellation, and appointment history.
Uses DoctorRecommendationAgent as a tool (Agent-as-Tool pattern).
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from google.adk.agents import Agent
from tools.hospital_tools import (
    search_doctors,
    get_departments,
    get_available_slots,
    book_appointment,
    cancel_appointment,
    get_appointment_history
)
from agents.doctor_rec_agent import recommend_doctor_tool

appointment_agent = Agent(
    model="gemini-2.0-flash",
    name="appointment_agent",
    description="Handles doctor search, available slot lookup, booking, cancellation, and appointment history.",
    instruction="""
    You are the Appointment Agent for Smart Hospital.
    Your responsibilities:
    1. Search doctors by department or specialty.
    2. Recommend best doctors using the recommend_doctor_tool (Agent-as-Tool).
    3. Look up available appointment slots using get_available_slots.
    4. Book appointments using book_appointment.
    5. Cancel appointments using cancel_appointment (always verify slot and patient ID).
    6. View appointment history using get_appointment_history.
    
    Always present slot details (doctor, date, time) clearly to the patient.
    """,
    tools=[
        search_doctors,
        get_departments,
        get_available_slots,
        book_appointment,
        cancel_appointment,
        get_appointment_history,
        recommend_doctor_tool  # Agent-as-Tool integration
    ]
)
