"""MCP Package for Smart Hospital."""
from .server import HospitalMCPServer, mcp_server_instance
from .client import HospitalMCPClient

__all__ = ["HospitalMCPServer", "mcp_server_instance", "HospitalMCPClient"]
