"""
Phase 1 Verification Tests.
Uses standard Python unittest framework to verify schemas, OpenAPI spec, and mock API operations.
"""
import sys
import os
import unittest

# Ensure smart-hospital package root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from schemas.models import Doctor, Slot, Appointment, DocumentSummary, PatientRecord
from api.mock_server import HospitalAPIBackend

class TestPhase1(unittest.TestCase):

    def test_pydantic_schemas_instantiation(self):
        """Verify all Phase 1 Pydantic data schemas instantiate correctly."""
        doc = Doctor(
            id="DOC-101",
            name="Dr. Sarah Jenkins",
            department="Dermatology",
            experience_years=12,
            rating=4.9,
            bio="Dermatologist specialist."
        )
        self.assertEqual(doc.id, "DOC-101")
        self.assertEqual(doc.department, "Dermatology")

        slot = Slot(
            slot_id="SLOT-001",
            doctor_id="DOC-101",
            doctor_name="Dr. Sarah Jenkins",
            department="Dermatology",
            date="2026-09-20",
            time="09:30 AM",
            available=True
        )
        self.assertTrue(slot.available)

        app = Appointment(
            appointment_id="APP-9001",
            patient_id="PAT-1001",
            doctor_id="DOC-101",
            doctor_name="Dr. Sarah Jenkins",
            department="Dermatology",
            date="2026-08-12",
            time="10:00 AM",
            status="confirmed"
        )
        self.assertEqual(app.status, "confirmed")

    def test_openapi_spec_validity(self):
        """Verify openapi.yaml exists and contains required OpenAPI path definitions."""
        openapi_path = os.path.join(os.path.dirname(__file__), "..", "api", "openapi.yaml")
        self.assertTrue(os.path.exists(openapi_path), "openapi.yaml should exist")
        
        with open(openapi_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        self.assertIn("Smart Hospital Operations API", content)
        self.assertIn("/doctors", content)
        self.assertIn("/slots", content)
        self.assertIn("/appointments", content)

    def test_mock_api_operations(self):
        """Verify Mock Hospital API backend methods perform correctly."""
        # Test doctor search
        dermatologists = HospitalAPIBackend.search_doctors(department="Dermatology")
        self.assertGreaterEqual(len(dermatologists), 1)
        self.assertEqual(dermatologists[0]["name"], "Dr. Sarah Jenkins")

        # Test departments list
        departments = HospitalAPIBackend.get_departments()
        self.assertGreaterEqual(len(departments), 5)

        # Test slots retrieval
        slots = HospitalAPIBackend.get_available_slots(department="Dermatology")
        self.assertGreaterEqual(len(slots), 1)

        # Test booking appointment
        res = HospitalAPIBackend.book_appointment(
            patient_id="PAT-1001",
            doctor_id="DOC-101",
            slot_id=slots[0]["slot_id"],
            notes="Testing Phase 1 booking"
        )
        self.assertTrue(res.get("success"))
        booked_app = res.get("appointment")
        self.assertEqual(booked_app["doctor_id"], "DOC-101")

        # Test appointment history
        history = HospitalAPIBackend.get_appointment_history("PAT-1001")
        self.assertGreaterEqual(len(history), 2)

        # Test cancellation
        cancel_res = HospitalAPIBackend.cancel_appointment(booked_app["appointment_id"])
        self.assertTrue(cancel_res.get("success"))

    def test_general_physicians_search(self):
        """Verify General Physician doctors exist and Pediatrics is removed."""
        gps = HospitalAPIBackend.search_doctors(department="General Physician")
        self.assertEqual(len(gps), 2)
        gp_names = [d["name"] for d in gps]
        self.assertIn("Dr. David Miller", gp_names)
        self.assertIn("Dr. Priya Sharma", gp_names)

        # Confirm Pediatrics was removed
        pediatrics = HospitalAPIBackend.search_doctors(department="Pediatrics")
        self.assertEqual(len(pediatrics), 0)

if __name__ == "__main__":
    unittest.main()
