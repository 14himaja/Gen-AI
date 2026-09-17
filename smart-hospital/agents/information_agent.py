"""
Information Agent for Smart Hospital.
Answers general hospital Q&A, department descriptions, procedure prep instructions, and test definitions.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from google.adk.agents import Agent
from tools.hospital_tools import get_departments

information_agent = Agent(
    model="gemini-2.0-flash",
    name="information_agent",
    description="Answers general questions regarding hospital departments, procedures, test definitions, and preparation instructions.",
    instruction="""
    You are the Information Agent for Smart Hospital.
    Your responsibilities:
    1. Answer general patient inquiries (e.g. 'What does cardiology handle?', 'What is an ECG?', 'What should I bring?').
    2. Retrieve hospital department locations and extensions using get_departments tool.
    3. Provide helpful prep guidance for common procedures.
    
    ⚠️ Mandatory Rule: Provide general educational info only. Do NOT provide personal medical diagnoses.
    """,
    tools=[get_departments]
)
