"""
Google ADK Function Tools for Smart Hospital Operations.
Exposes standard Python functions as ADK tools for agents.
"""
from typing import List, Dict, Any, Optional
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api.mock_server import HospitalAPIBackend
from mcp.client import mcp_client_instance

def search_doctors(department: Optional[str] = None, query: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Search for doctors by department or keyword.
    
    Args:
        department: Optional department name (e.g. 'Dermatology', 'General Physician', 'Cardiology')
        query: Optional search keyword matching doctor name or bio
    """
    return HospitalAPIBackend.search_doctors(department=department, query=query)

def get_departments() -> List[Dict[str, Any]]:
    """Retrieve all hospital departments with descriptions, locations, and contact extensions."""
    return HospitalAPIBackend.get_departments()

def get_available_slots(doctor_id: Optional[str] = None, department: Optional[str] = None, date: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get available appointment time slots.
    
    Args:
        doctor_id: Optional doctor ID (e.g. 'DOC-101')
        department: Optional department name
        date: Optional date filter (YYYY-MM-DD)
    """
    return HospitalAPIBackend.get_available_slots(doctor_id=doctor_id, department=department, date=date)

def book_appointment(patient_id: str, doctor_id: str, slot_id: str, notes: Optional[str] = "") -> Dict[str, Any]:
    """
    Book a new hospital appointment.
    
    Args:
        patient_id: Unique Patient ID (e.g. 'PAT-1001')
        doctor_id: Unique Doctor ID (e.g. 'DOC-106')
        slot_id: Selected Slot ID (e.g. 'SLOT-007')
        notes: Reason for visit or notes
    """
    return HospitalAPIBackend.book_appointment(patient_id=patient_id, doctor_id=doctor_id, slot_id=slot_id, notes=notes)

def cancel_appointment(appointment_id: str) -> Dict[str, Any]:
    """
    Cancel an existing appointment.
    
    Args:
        appointment_id: Appointment ID to cancel (e.g. 'APP-9001')
    """
    return HospitalAPIBackend.cancel_appointment(appointment_id=appointment_id)

def get_appointment_history(patient_id: str = "PAT-1001") -> List[Dict[str, Any]]:
    """
    Retrieve past and upcoming appointment history for a patient.
    
    Args:
        patient_id: Patient ID
    """
    return HospitalAPIBackend.get_appointment_history(patient_id=patient_id)

def read_document(doc_id: str, patient_id: str = "PAT-1001") -> Dict[str, Any]:
    """
    Read text content of an uploaded medical document (prescription, lab report, discharge summary).
    
    Args:
        doc_id: Document ID (e.g. 'DOC-FILE-1')
        patient_id: Patient ID
    """
    docs = HospitalAPIBackend.get_patient_documents(patient_id=patient_id)
    doc = next((d for d in docs if d["doc_id"] == doc_id), None)
    if not doc:
        return {"error": f"Document ID '{doc_id}' not found."}
    return doc

def search_patient_records(patient_id: str = "PAT-1001") -> Dict[str, Any]:
    """
    Retrieve historical medical records, allergies, and patient profile details.
    
    Args:
        patient_id: Patient ID
    """
    return HospitalAPIBackend.get_patient_record(patient_id=patient_id)

def create_summary(patient_id: str, summary_content: str) -> Dict[str, Any]:
    """
    Save and format a doctor visit summary report via MCP.
    
    Args:
        patient_id: Patient ID
        summary_content: Formatted visit summary text
    """
    return mcp_client_instance.execute_tool("save_summary", patient_id=patient_id, summary=summary_content)
