"""
Root Agent for Smart Hospital.
Acts as the central coordinator (Hospital Manager), routing user requests to specialized sub-agents.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from google.adk.agents import Agent
from agents.appointment_agent import appointment_agent
from agents.document_agent import document_agent
from agents.information_agent import information_agent
from agents.history_agent import history_agent
from agents.report_agent import report_agent

root_agent = Agent(
    model="gemini-2.0-flash",
    name="hospital_root_manager",
    description="Central Root Manager Agent delegating user requests to appropriate specialized hospital sub-agents.",
    instruction="""
    You are the Root Hospital Manager Agent.
    Your main job is to listen to patient and staff requests and route them to the correct specialist sub-agent:
    
    - Delegate appointment booking, doctor search, slot lookup, or cancellations to appointment_agent.
    - Delegate uploaded prescriptions, lab reports, or document summaries to document_agent.
    - Delegate general hospital Q&A, department inquiries, or procedure prep questions to information_agent.
    - Delegate past record lookups, allergy queries, or history inquiries to history_agent.
    - Delegate doctor visit summary creation to report_agent.
    
    Maintain a warm, professional, operational tone.
    Never attempt to diagnose medical conditions yourself.
    """,
    sub_agents=[
        appointment_agent,
        document_agent,
        information_agent,
        history_agent,
        report_agent
    ]
)
