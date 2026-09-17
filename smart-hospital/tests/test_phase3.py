"""
Phase 3 Verification Tests.
Tests function tools, sub-agents initialization, Agent-as-Tool execution, and RootAgent delegation.
"""
import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tools.hospital_tools import (
    search_doctors,
    get_departments,
    get_available_slots,
    book_appointment,
    read_document,
    search_patient_records
)
from agents.doctor_rec_agent import doctor_rec_agent, recommend_doctor_tool
from agents.appointment_agent import appointment_agent
from agents.document_agent import document_agent
from agents.information_agent import information_agent
from agents.history_agent import history_agent
from agents.report_agent import report_agent
from agents.root_agent import root_agent

class TestPhase3(unittest.TestCase):

    def test_function_tools_execution(self):
        """Verify all Phase 3 ADK function tools execute cleanly."""
        docs = search_doctors(department="General Physician")
        self.assertGreaterEqual(len(docs), 1)

        depts = get_departments()
        self.assertGreaterEqual(len(depts), 5)

        slots = get_available_slots(department="General Physician")
        self.assertGreaterEqual(len(slots), 1)

        doc_data = read_document("DOC-FILE-1", "PAT-1001")
        self.assertEqual(doc_data["doc_type"], "prescription")

        record = search_patient_records("PAT-1001")
        self.assertEqual(record["patient_id"], "PAT-1001")

    def test_agent_as_tool_pattern(self):
        """Verify DoctorRecommendationAgent wrapped as a tool (Agent-as-Tool) executes correctly."""
        rec = recommend_doctor_tool(department="General Physician")
        self.assertIn("recommended_doctor", rec)
        self.assertIn(rec["recommended_doctor"], ["Dr. David Miller", "Dr. Priya Sharma"])

    def test_sub_agents_instantiation(self):
        """Verify all 5 specialized sub-agents and RootAgent instantiate correctly with ADK properties."""
        self.assertEqual(appointment_agent.name, "appointment_agent")
        self.assertEqual(document_agent.name, "document_agent")
        self.assertEqual(information_agent.name, "information_agent")
        self.assertEqual(history_agent.name, "history_agent")
        self.assertEqual(report_agent.name, "report_agent")
        
        # Check RootAgent sub_agents hierarchy
        self.assertEqual(root_agent.name, "hospital_root_manager")
        sub_names = [a.name for a in root_agent.sub_agents]
        self.assertIn("appointment_agent", sub_names)
        self.assertIn("document_agent", sub_names)
        self.assertIn("information_agent", sub_names)
        self.assertIn("history_agent", sub_names)
        self.assertIn("report_agent", sub_names)

if __name__ == "__main__":
    unittest.main()
