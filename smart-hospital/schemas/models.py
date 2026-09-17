"""
Pydantic Data Schemas for Smart Hospital Operations.
Defines structured data models used for Google ADK structured outputs (response_schema),
API payloads, appointments, document processing, and state management.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class Doctor(BaseModel):
    id: str = Field(..., description="Unique ID of the doctor (e.g., DOC-101)")
    name: str = Field(..., description="Full name of the doctor")
    department: str = Field(..., description="Department or medical specialty")
    experience_years: int = Field(..., description="Years of clinical experience")
    rating: float = Field(default=4.8, description="Patient satisfaction rating out of 5.0")
    bio: str = Field(..., description="Short biography and area of expertise")

class Slot(BaseModel):
    slot_id: str = Field(..., description="Unique slot identifier (e.g., SLOT-001)")
    doctor_id: str = Field(..., description="Doctor ID associated with this slot")
    doctor_name: str = Field(..., description="Doctor's full name")
    department: str = Field(..., description="Hospital department")
    date: str = Field(..., description="Date of slot (YYYY-MM-DD)")
    time: str = Field(..., description="Time of slot (e.g., 09:30 AM)")
    available: bool = Field(default=True, description="Whether the slot is currently available")

class Appointment(BaseModel):
    appointment_id: str = Field(..., description="Unique appointment ID (e.g., APP-9001)")
    patient_id: str = Field(..., description="Patient ID")
    doctor_id: str = Field(..., description="Doctor ID")
    doctor_name: str = Field(..., description="Doctor name")
    department: str = Field(..., description="Department name")
    date: str = Field(..., description="Appointment date (YYYY-MM-DD)")
    time: str = Field(..., description="Appointment time slot")
    status: str = Field(default="confirmed", description="Status: confirmed, pending, or cancelled")
    notes: Optional[str] = Field(None, description="Additional notes or reason for visit")

class MedicalDocument(BaseModel):
    doc_id: str = Field(..., description="Unique document ID (e.g., DOC-FILE-1)")
    patient_id: str = Field(..., description="Patient ID")
    doc_type: str = Field(..., description="Document type: prescription, lab_report, discharge_summary")
    title: str = Field(..., description="Document title or filename")
    upload_date: str = Field(..., description="Upload date (YYYY-MM-DD)")
    content: str = Field(..., description="Extracted plain text content of the medical document")
    quality_score: float = Field(default=1.0, description="Readability score between 0.0 and 1.0")

class ExtractedFact(BaseModel):
    category: str = Field(..., description="Category: medicine, test_result, diagnosis_note, instruction")
    fact: str = Field(..., description="Extracted factual statement")
    confidence: float = Field(default=0.95, description="Extraction confidence score")

class DocumentSummary(BaseModel):
    doc_id: str = Field(..., description="Document ID processed")
    document_type: str = Field(..., description="Type of medical document")
    date: str = Field(..., description="Document date")
    extracted_information: List[ExtractedFact] = Field(..., description="Extracted facts list")
    warnings: List[str] = Field(default_factory=list, description="Quality warnings or missing information alerts")
    disclaimer: str = Field(
        default="⚠️ Operational assistant document extraction. This is not a medical diagnosis.",
        description="Mandatory non-diagnosis medical disclaimer"
    )

class PatientRecord(BaseModel):
    patient_id: str = Field(..., description="Unique Patient ID")
    name: str = Field(..., description="Patient full name")
    age: int = Field(..., description="Patient age in years")
    gender: str = Field(..., description="Patient gender")
    allergies: List[str] = Field(default_factory=list, description="Known allergies")
    medical_history_summary: List[str] = Field(default_factory=list, description="Historical medical events")

class ReportSummary(BaseModel):
    patient_id: str = Field(..., description="Patient ID")
    generated_at: str = Field(..., description="Timestamp of report generation")
    upcoming_appointment: Optional[Dict[str, Any]] = Field(None, description="Details of upcoming appointment if any")
    previous_appointments_count: int = Field(0, description="Count of past appointments")
    recent_documents_summary: List[Dict[str, Any]] = Field(default_factory=list, description="Summarized document details")
    doctor_notes_summary: str = Field("", description="Operational summary notes for the doctor")
    disclaimer: str = Field(
        default="⚠️ This report is an operational summary for doctor visits. It is not a medical diagnosis.",
        description="Mandatory medical non-diagnosis disclaimer"
    )

class SessionState(BaseModel):
    patient_id: str = "PAT-1001"
    selected_department: Optional[str] = None
    selected_doctor: Optional[str] = None
    selected_slot: Optional[str] = None
    appointment_status: str = "idle"
    current_workflow: Optional[str] = None
    uploaded_doc_ids: List[str] = Field(default_factory=list)
    active_dialogue_stage: str = "greeting"

class PatientPreferences(BaseModel):
    patient_id: str = "PAT-1001"
    preferred_hospital: str = "ABC Central Hospital"
    preferred_department: str = "Dermatology"
    preferred_time_slot: str = "Morning (9:00 AM - 12:00 PM)"
    preferred_doctor: Optional[str] = "Dr. Sarah Jenkins"
    preferred_communication_lang: str = "English"
