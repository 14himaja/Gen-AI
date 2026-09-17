"""
Session State Manager for Smart Hospital.
Demonstrates Google ADK Concept #6: Session State.
Tracks active conversation state during a user session.
"""
import sys
import os
from typing import Dict, Any, Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from schemas.models import SessionState

class HospitalSessionStateManager:
    """
    Manages active session state for patient dialogues.
    Tracks state such as:
      state = {
          "patient_id": "PAT-1001",
          "selected_department": "General Physician",
          "selected_doctor": "DOC-106",
          "selected_slot": "SLOT-007",
          "appointment_status": "pending"
      }
    """
    def __init__(self):
        self.sessions: Dict[str, SessionState] = {}

    def get_session(self, session_id: str) -> SessionState:
        """Retrieve active session state or initialize new default state."""
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionState(patient_id="PAT-1001")
        return self.sessions[session_id]

    def update_session(self, session_id: str, **kwargs) -> SessionState:
        """Update fields in active session state."""
        session = self.get_session(session_id)
        for key, value in kwargs.items():
            if hasattr(session, key):
                setattr(session, key, value)
        return session

    def reset_session(self, session_id: str) -> SessionState:
        """Reset session state to default."""
        self.sessions[session_id] = SessionState(patient_id="PAT-1001")
        return self.sessions[session_id]

# Global singleton manager
session_state_manager = HospitalSessionStateManager()
