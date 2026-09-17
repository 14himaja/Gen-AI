"""
Master Test Suite for Smart Hospital Assistant.
Verifies all 13 Google ADK concepts end-to-end.
"""
import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Concept 1: Multi-Agent System & Concept 11: Agent-as-Tool
from agents.root_agent import root_agent
from agents.appointment_agent import appointment_agent
from agents.document_agent import document_agent
from agents.information_agent import information_agent
from agents.history_agent import history_agent
from agents.report_agent import report_agent
from agents.doctor_rec_agent import recommend_doctor_tool

# Concept 2: Function Tools
from tools.hospital_tools import search_doctors, get_available_slots, book_appointment, cancel_appointment

# Concept 3, 4, 5: Workflows
from workflows.sequential_workflow import run_sequential_workflow
from workflows.parallel_workflow import run_parallel_workflow
from workflows.loop_workflow import run_document_quality_loop

# Concept 6: Session State & Concept 7: Long-Term Memory
from state_memory.session_state import session_state_manager
from state_memory.long_term_memory import memory_store_instance

# Concept 8: Structured Output & Concept 10: OpenAPI
from schemas.models import DocumentSummary, ReportSummary

# Concept 9: MCP
from mcp.server import mcp_server_instance
from mcp.client import mcp_client_instance

# Concept 12: Callbacks & Concept 13: Guardrails
from callbacks.security import (
    before_agent_authorization_callback,
    before_model_pii_redaction_callback,
    before_tool_action_confirmation_callback,
    enforce_medical_non_diagnosis_guardrail
)

class MockCallbackContext:
    def __init__(self, state_dict):
        self.state = state_dict

class TestMasterADKCoverage(unittest.TestCase):

    def test_01_multi_agent_system(self):
        """Concept 1: Multi-Agent System hierarchy."""
        self.assertEqual(root_agent.name, "hospital_root_manager")
        sub_names = [a.name for a in root_agent.sub_agents]
        self.assertIn("appointment_agent", sub_names)
        self.assertIn("document_agent", sub_names)
        self.assertIn("information_agent", sub_names)
        self.assertIn("history_agent", sub_names)
        self.assertIn("report_agent", sub_names)

    def test_02_function_tools(self):
        """Concept 2: Function Tools."""
        docs = search_doctors(department="General Physician")
        self.assertGreaterEqual(len(docs), 1)

        slots = get_available_slots(department="General Physician")
        self.assertGreaterEqual(len(slots), 1)

    def test_03_sequential_workflow(self):
        """Concept 3: Sequential Workflow (SequentialAgent)."""
        res = run_sequential_workflow("PAT-1001", "DOC-FILE-1")
        self.assertEqual(res["status"], "completed")
        self.assertEqual(res["workflow"], "sequential")

    def test_04_parallel_workflow(self):
        """Concept 4: Parallel Workflow (ParallelAgent)."""
        res = run_parallel_workflow("PAT-1001", "DOC-FILE-1")
        self.assertEqual(res["status"], "completed")
        self.assertEqual(res["workflow"], "parallel")

    def test_05_loop_workflow(self):
        """Concept 5: Loop Workflow (LoopAgent)."""
        res = run_document_quality_loop("DOC-FILE-1", "PAT-1001")
        self.assertEqual(res["status"], "APPROVED")

    def test_06_session_state(self):
        """Concept 6: Session State."""
        state = session_state_manager.get_session("SESS-TEST")
        self.assertEqual(state.patient_id, "PAT-1001")
        updated = session_state_manager.update_session("SESS-TEST", selected_doctor="DOC-106")
        self.assertEqual(updated.selected_doctor, "DOC-106")

    def test_07_memory(self):
        """Concept 7: Long-Term Memory."""
        prefs = memory_store_instance.get_preferences("PAT-1001")
        self.assertEqual(prefs.preferred_department, "General Physician")
        usual = memory_store_instance.get_usual_appointment_context("PAT-1001")
        self.assertEqual(usual["doctor"], "Dr. David Miller")

    def test_08_structured_output(self):
        """Concept 8: Structured Output Pydantic Schemas."""
        self.assertEqual(document_agent.output_schema, DocumentSummary)
        self.assertEqual(report_agent.output_schema, ReportSummary)

    def test_09_mcp(self):
        """Concept 9: MCP Server & Client."""
        mcp_tools = mcp_client_instance.get_available_tools()
        names = [t["name"] for t in mcp_tools]
        self.assertIn("search_doctors", names)
        res = mcp_client_instance.execute_tool("search_doctors", department="General Physician")
        self.assertIn("doctors", res)

    def test_10_openapi(self):
        """Concept 10: OpenAPI Spec."""
        openapi_path = os.path.join(os.path.dirname(__file__), "..", "api", "openapi.yaml")
        self.assertTrue(os.path.exists(openapi_path))

    def test_11_agent_as_tool(self):
        """Concept 11: Agent-as-Tool Pattern."""
        rec = recommend_doctor_tool(department="General Physician")
        self.assertIn("recommended_doctor", rec)
        self.assertIn(rec["recommended_doctor"], ["Dr. David Miller", "Dr. Priya Sharma"])

    def test_12_callbacks(self):
        """Concept 12: Callbacks (Auth, PII Redaction, Tool Confirmation)."""
        ctx_auth = MockCallbackContext(state_dict={"patient_id": "PAT-1001", "is_authorized": True})
        self.assertIsNone(before_agent_authorization_callback(ctx_auth))

        pii_clean = before_model_pii_redaction_callback("SSN is 123-45-6789")
        self.assertIn("[REDACTED_SSN]", pii_clean)

        conf_res = before_tool_action_confirmation_callback("cancel_appointment", {}, user_confirmed=False)
        self.assertTrue(conf_res["blocked"])

    def test_13_guardrails(self):
        """Concept 13: Safety Guardrails."""
        guarded = enforce_medical_non_diagnosis_guardrail("Operational recommendation for Dr. David Miller.")
        self.assertIn("Disclaimer:", guarded)
        self.assertIn("does not provide medical diagnoses", guarded)

if __name__ == "__main__":
    unittest.main()
