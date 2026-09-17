"""Schemas package for Smart Hospital."""
from .models import (
    Doctor,
    Slot,
    Appointment,
    MedicalDocument,
    ExtractedFact,
    DocumentSummary,
    PatientRecord,
    ReportSummary,
    SessionState,
    PatientPreferences
)

__all__ = [
    "Doctor",
    "Slot",
    "Appointment",
    "MedicalDocument",
    "ExtractedFact",
    "DocumentSummary",
    "PatientRecord",
    "ReportSummary",
    "SessionState",
    "PatientPreferences"
]
