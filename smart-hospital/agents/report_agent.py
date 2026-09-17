"""
Report Agent for Smart Hospital.
Aggregates records, documents, and appointment data into a structured Doctor Visit Summary report.
Enforces Pydantic ReportSummary response schema.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from google.adk.agents import Agent
from tools.hospital_tools import create_summary
from schemas.models import ReportSummary

report_agent = Agent(
    model="gemini-2.0-flash",
    name="report_agent",
    description="Combines historical records, document facts, and appointment details into a comprehensive Doctor Visit Summary report.",
    instruction="""
    You are the Report Agent for Smart Hospital.
    Your responsibilities:
    1. Synthesize patient history, recent document summaries, and upcoming appointment data.
    2. Format a comprehensive operational Patient Visit Summary report for attending doctors.
    3. Save the report via create_summary tool.
    4. Ensure the output strictly conforms to the ReportSummary schema.
    
    ⚠️ Mandatory Rule: Include non-diagnosis disclaimer on all generated reports.
    """,
    tools=[create_summary],
    output_schema=ReportSummary,
    output_key="report_summary"
)
