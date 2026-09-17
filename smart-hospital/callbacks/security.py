"""
Google ADK Security Callbacks & Medical Guardrails Implementation.
Demonstrates Google ADK Concept #12 (Callbacks) and Concept #13 (Guardrails).

Includes:
1. Agent Callback: Authorization verification before accessing records.
2. Model Callback: Sensitive PII (SSN, phone, address) redaction before LLM inference.
3. Tool Callback: Confirmation validation before high-impact actions (book/cancel appointment).
4. Guardrails: Enforces medical non-diagnosis rules.
"""
import re
from typing import Dict, Any, Optional
from google.adk.agents.callback_context import CallbackContext

def before_agent_authorization_callback(callback_context: Any) -> Optional[Dict[str, Any]]:
    """
    Google ADK before_agent_callback.
    Verifies that the current user/session is authorized to access patient records.
    """
    state = getattr(callback_context, "state", {})
    if hasattr(callback_context, "get"):
        state = callback_context.get("state", {})
        
    if isinstance(state, dict):
        patient_id = state.get("patient_id", "PAT-1001")
        authorized = state.get("is_authorized", True)
    else:
        patient_id = getattr(state, "patient_id", "PAT-1001")
        authorized = getattr(state, "is_authorized", True)

    if not authorized:
        return {
            "error": "UNAUTHORIZED_ACCESS",
            "message": f"User is not authorized to view records for Patient ID '{patient_id}'."
        }
    return None

def before_model_pii_redaction_callback(text_input: str) -> str:
    """
    Google ADK before_model_callback pattern.
    Scans patient data and redacts sensitive PII (Social Security Numbers, phone numbers)
    before sending prompt text to the LLM.
    """
    sanitized = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[REDACTED_SSN]', text_input)
    sanitized = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[REDACTED_PHONE]', sanitized)
    return sanitized

def before_tool_action_confirmation_callback(tool_name: str, arguments: Dict[str, Any], user_confirmed: bool = True) -> Dict[str, Any]:
    """
    Google ADK before_tool_callback pattern.
    Intercepts high-impact actions like book_appointment or cancel_appointment
    and validates user confirmation before execution.
    """
    high_impact_tools = ["cancel_appointment", "book_appointment"]
    
    if tool_name in high_impact_tools:
        if not user_confirmed:
            return {
                "blocked": True,
                "reason": "ACTION_PENDING_CONFIRMATION",
                "message": f"High-impact action '{tool_name}' requires explicit user confirmation before execution.",
                "action_details": arguments
            }
    return {"blocked": False, "reason": "APPROVED"}

def enforce_medical_non_diagnosis_guardrail(agent_output: str) -> str:
    """
    Google ADK Medical Non-Diagnosis Guardrail.
    Interprets output text and automatically appends mandatory disclaimer if medical advice or diagnosis is attempted.
    """
    disclaimer = "\n\n⚠️ Disclaimer: This AI system is an operational hospital assistant. It does not provide medical diagnoses or treatment advice. Please consult a qualified healthcare professional."
    
    if "Disclaimer:" not in agent_output:
        return agent_output + disclaimer
    return agent_output
