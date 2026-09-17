"""
Phase 6 Verification Tests.
Tests Authorization Callback, PII Redaction Model Callback, Action Confirmation Tool Callback, and Non-Diagnosis Guardrails.
"""
import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from callbacks.security import (
    before_agent_authorization_callback,
    before_model_pii_redaction_callback,
    before_tool_action_confirmation_callback,
    enforce_medical_non_diagnosis_guardrail
)

class MockCallbackContext:
    def __init__(self, state_dict):
        self.state = state_dict

class TestPhase6(unittest.TestCase):

    def test_authorization_callback(self):
        """Verify Authorization Callback allows authorized access and blocks unauthorized access."""
        # Test authorized state
        ctx_authorized = MockCallbackContext(state_dict={"patient_id": "PAT-1001", "is_authorized": True})
        res_auth = before_agent_authorization_callback(ctx_authorized)
        self.assertIsNone(res_auth)

        # Test unauthorized state
        ctx_unauthorized = MockCallbackContext(state_dict={"patient_id": "PAT-9999", "is_authorized": False})
        res_unauth = before_agent_authorization_callback(ctx_unauthorized)
        self.assertIsNotNone(res_unauth)
        self.assertEqual(res_unauth["error"], "UNAUTHORIZED_ACCESS")

    def test_pii_redaction_callback(self):
        """Verify Model Callback redacts SSNs and phone numbers before LLM inference."""
        raw_text = "Patient SSN is 123-45-6789 and phone number is 555-123-4567."
        redacted = before_model_pii_redaction_callback(raw_text)
        self.assertNotIn("123-45-6789", redacted)
        self.assertNotIn("555-123-4567", redacted)
        self.assertIn("[REDACTED_SSN]", redacted)
        self.assertIn("[REDACTED_PHONE]", redacted)

    def test_tool_action_confirmation_callback(self):
        """Verify Tool Callback blocks high-impact actions when confirmation is missing."""
        # Unconfirmed cancellation
        res_blocked = before_tool_action_confirmation_callback(
            tool_name="cancel_appointment",
            arguments={"appointment_id": "APP-9001"},
            user_confirmed=False
        )
        self.assertTrue(res_blocked["blocked"])
        self.assertEqual(res_blocked["reason"], "ACTION_PENDING_CONFIRMATION")

        # Confirmed cancellation
        res_approved = before_tool_action_confirmation_callback(
            tool_name="cancel_appointment",
            arguments={"appointment_id": "APP-9001"},
            user_confirmed=True
        )
        self.assertFalse(res_approved["blocked"])

    def test_medical_non_diagnosis_guardrail(self):
        """Verify Non-Diagnosis Guardrail appends mandatory medical disclaimer."""
        raw_response = "You should schedule a consultation with Dr. Sarah Jenkins for eczema evaluation."
        guarded = enforce_medical_non_diagnosis_guardrail(raw_response)
        self.assertIn("Disclaimer:", guarded)
        self.assertIn("does not provide medical diagnoses", guarded)

if __name__ == "__main__":
    unittest.main()
