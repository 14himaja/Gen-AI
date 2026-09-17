"""
Phase 5 Verification Tests.
Tests Session State Manager and Long-Term Preference Memory Store.
"""
import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from state_memory.session_state import session_state_manager
from state_memory.long_term_memory import memory_store_instance

class TestPhase5(unittest.TestCase):

    def test_session_state_lifecycle(self):
        """Verify active conversation session state get, update, and reset operations."""
        sid = "SESSION-TEST-123"
        state = session_state_manager.get_session(sid)
        self.assertEqual(state.patient_id, "PAT-1001")
        self.assertEqual(state.appointment_status, "idle")

        updated = session_state_manager.update_session(
            sid,
            selected_department="General Physician",
            selected_doctor="DOC-106",
            selected_slot="SLOT-007",
            appointment_status="pending"
        )
        self.assertEqual(updated.selected_department, "General Physician")
        self.assertEqual(updated.selected_doctor, "DOC-106")
        self.assertEqual(updated.appointment_status, "pending")

        reset = session_state_manager.reset_session(sid)
        self.assertEqual(reset.appointment_status, "idle")

    def test_long_term_memory_preferences(self):
        """Verify long-term preference memory retrieval and 'Book my usual appointment' context."""
        pid = "PAT-1001"
        prefs = memory_store_instance.get_preferences(pid)
        self.assertEqual(prefs.preferred_department, "General Physician")
        self.assertEqual(prefs.preferred_doctor, "Dr. David Miller")

        usual_context = memory_store_instance.get_usual_appointment_context(pid)
        self.assertEqual(usual_context["department"], "General Physician")
        self.assertEqual(usual_context["doctor"], "Dr. David Miller")

        # Test setting a preference
        memory_store_instance.set_preference(pid, "preferred_department", "Dermatology")
        updated_prefs = memory_store_instance.get_preferences(pid)
        self.assertEqual(updated_prefs.preferred_department, "Dermatology")

if __name__ == "__main__":
    unittest.main()
