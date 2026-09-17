"""
Model Context Protocol (MCP) Server for Smart Hospital Operations.
Exposes standard hospital tools to ADK agents over the MCP interface.
"""
from typing import Dict, Any, List, Optional
import sys
import os

# Ensure package path is available
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api.mock_server import HospitalAPIBackend

class HospitalMCPServer:
    """
    Model Context Protocol (MCP) Server exposing hospital operations to ADK agents.
    Exposes tools:
      - search_doctors
      - get_slots
      - get_appointments
      - get_patient_documents
      - save_summary
      - get_patient_history
    """
    def __init__(self):
        self.name = "Hospital-MCP-Server"
        self.version = "1.0.0"

    def list_tools(self) -> List[Dict[str, str]]:
        """List all tools exposed by the MCP server."""
        return [
            {"name": "search_doctors", "description": "Search for doctors by department or query string"},
            {"name": "get_slots", "description": "Get available appointment slots"},
            {"name": "get_appointments", "description": "Retrieve patient appointment history"},
            {"name": "get_patient_documents", "description": "Fetch uploaded medical documents for patient"},
            {"name": "save_summary", "description": "Save generated doctor visit summary"},
            {"name": "get_patient_history", "description": "Retrieve patient medical history and allergy records"}
        ]

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool call via the MCP server."""
        if tool_name == "search_doctors":
            return {"doctors": HospitalAPIBackend.search_doctors(
                department=arguments.get("department"),
                query=arguments.get("query")
            )}
        elif tool_name == "get_slots":
            return {"slots": HospitalAPIBackend.get_available_slots(
                doctor_id=arguments.get("doctor_id"),
                department=arguments.get("department"),
                date=arguments.get("date")
            )}
        elif tool_name == "get_appointments":
            return {"appointments": HospitalAPIBackend.get_appointment_history(
                patient_id=arguments.get("patient_id", "PAT-1001")
            )}
        elif tool_name == "get_patient_documents":
            return {"documents": HospitalAPIBackend.get_patient_documents(
                patient_id=arguments.get("patient_id", "PAT-1001")
            )}
        elif tool_name == "save_summary":
            return {
                "status": "saved",
                "summary_id": "SUM-8802",
                "summary": arguments.get("summary")
            }
        elif tool_name == "get_patient_history":
            return {"record": HospitalAPIBackend.get_patient_record(
                patient_id=arguments.get("patient_id", "PAT-1001")
            )}
        else:
            return {"error": f"Unknown tool: {tool_name}"}

# Global singleton instance
mcp_server_instance = HospitalMCPServer()
