"""
Model Context Protocol (MCP) Client for Smart Hospital Operations.
Acts as the interface for Google ADK agents to invoke tools exposed by the MCP Server.
"""
from typing import Dict, Any, List, Optional
from mcp.server import mcp_server_instance, HospitalMCPServer

class HospitalMCPClient:
    """
    Client connecting ADK Agents to the Hospital MCP Server.
    Translates agent tool requests into standardized MCP protocol calls.
    """
    def __init__(self, server: Optional[HospitalMCPServer] = None):
        self.server = server or mcp_server_instance

    def get_available_tools(self) -> List[Dict[str, str]]:
        """Query server for list of available tools."""
        return self.server.list_tools()

    def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Execute a tool request through the MCP server."""
        return self.server.call_tool(tool_name, kwargs)

# Global client singleton
mcp_client_instance = HospitalMCPClient()
