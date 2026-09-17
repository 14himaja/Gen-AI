"""
Doctor Recommendation Agent & Agent-as-Tool Wrapper.
Demonstrates Google ADK Concept #11: Agent-as-Tool.
Specialized agent evaluating symptoms/needs to recommend the best matching doctor.
"""
import sys
import os
from typing import Dict, Any, Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from google.adk.agents import Agent
from tools.hospital_tools import search_doctors

# Specialized Agent for Doctor Recommendation
doctor_rec_agent = Agent(
    model="gemini-2.0-flash",
    name="doctor_recommendation_agent",
    description="Analyzes patient operational requirements to recommend matching hospital doctors.",
    instruction="""
    You are a specialized Doctor Recommendation Agent.
    Your role is to analyze user requests, symptoms description (operationally only, no medical diagnosis),
    and match them with appropriate hospital doctors and departments.
    
    Use the search_doctors tool to query available doctors.
    Always recommend based on specialty, experience, and patient ratings.
    """,
    tools=[search_doctors]
)

def recommend_doctor_tool(department: Optional[str] = None, symptom_keyword: Optional[str] = None) -> Dict[str, Any]:
    """
    Agent-as-Tool Wrapper Function.
    Allows the AppointmentAgent to invoke the DoctorRecommendationAgent as a tool capability.
    """
    doctors = search_doctors(department=department, query=symptom_keyword)
    if not doctors:
        return {"recommendation": "No matching doctor found for the specified criteria.", "doctors": []}
    
    # Select best doctor by rating and experience
    best_doc = max(doctors, key=lambda d: d.get("rating", 0.0) + d.get("experience_years", 0) * 0.1)
    return {
        "recommended_doctor": best_doc["name"],
        "department": best_doc["department"],
        "doctor_id": best_doc["id"],
        "reasoning": f"Recommended based on highest rating ({best_doc['rating']}/5.0) and {best_doc['experience_years']} years of experience in {best_doc['department']}.",
        "all_matching_doctors": [d["name"] for d in doctors]
    }
