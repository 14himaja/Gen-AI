"""
Phase 2 Verification Tests.
Tests MCP Server tool listing and tool execution via MCP Client.
"""
import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mcp.server import mcp_server_instance
from mcp.client import mcp_client_instance

class TestPhase2(unittest.TestCase):

    def test_mcp_server_tool_listing(self):
        """Verify MCP Server exposes the required hospital tools."""
        tools = mcp_server_instance.list_tools()
        tool_names = [t["name"] for t in tools]
        self.assertIn("search_doctors", tool_names)
        self.assertIn("get_slots", tool_names)
        self.assertIn("get_appointments", tool_names)
        self.assertIn("get_patient_documents", tool_names)
        self.assertIn("save_summary", tool_names)
        self.assertIn("get_patient_history", tool_names)

    def test_mcp_client_tool_execution(self):
        """Verify MCP Client can execute tools through MCP Server."""
        # Test search_doctors via MCP
        doc_res = mcp_client_instance.execute_tool("search_doctors", department="General Physician")
        self.assertIn("doctors", doc_res)
        self.assertGreaterEqual(len(doc_res["doctors"]), 1)

        # Test get_slots via MCP
        slots_res = mcp_client_instance.execute_tool("get_slots", department="General Physician")
        self.assertIn("slots", slots_res)
        self.assertGreaterEqual(len(slots_res["slots"]), 1)

        # Test get_patient_history via MCP
        history_res = mcp_client_instance.execute_tool("get_patient_history", patient_id="PAT-1001")
        self.assertIn("record", history_res)
        self.assertEqual(history_res["record"]["patient_id"], "PAT-1001")

        # Test get_patient_documents via MCP
        docs_res = mcp_client_instance.execute_tool("get_patient_documents", patient_id="PAT-1001")
        self.assertIn("documents", docs_res)
        self.assertGreaterEqual(len(docs_res["documents"]), 1)

if __name__ == "__main__":
    unittest.main()
