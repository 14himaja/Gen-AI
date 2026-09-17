"""
Long-Term Preference Memory Store for Smart Hospital.
Demonstrates Google ADK Concept #7: Memory.
Persists long-term patient preferences across conversations (preferred department, doctor, slot time, language).
"""
import sys
import os
from typing import Dict, Any, Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from schemas.models import PatientPreferences

class PatientMemoryStore:
    """
    Stores long-term user preferences across multiple sessions.
    Allows queries like "Book my usual appointment" to retrieve stored preferences.
    """
    def __init__(self):
        self.memory: Dict[str, PatientPreferences] = {
            "PAT-1001": PatientPreferences(
                patient_id="PAT-1001",
                preferred_hospital="ABC Central Hospital",
                preferred_department="General Physician",
                preferred_time_slot="Morning (9:00 AM - 12:00 PM)",
                preferred_doctor="Dr. David Miller",
                preferred_communication_lang="English"
            )
        }

    def get_preferences(self, patient_id: str) -> PatientPreferences:
        """Retrieve patient long-term preferences."""
        if patient_id not in self.memory:
            self.memory[patient_id] = PatientPreferences(patient_id=patient_id)
        return self.memory[patient_id]

    def set_preference(self, patient_id: str, key: str, value: Any) -> PatientPreferences:
        """Update a specific long-term preference."""
        prefs = self.get_preferences(patient_id)
        if hasattr(prefs, key):
            setattr(prefs, key, value)
        return prefs

    def get_usual_appointment_context(self, patient_id: str) -> Dict[str, str]:
        """Synthesize 'Book my usual appointment' context from stored preferences."""
        prefs = self.get_preferences(patient_id)
        return {
            "department": prefs.preferred_department,
            "doctor": prefs.preferred_doctor or "First Available",
            "preferred_time": prefs.preferred_time_slot,
            "hospital": prefs.preferred_hospital
        }

# Global memory store instance
memory_store_instance = PatientMemoryStore()
