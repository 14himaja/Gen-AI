"""
Mock Hospital REST API Engine & Data Store.
Provides mock data and backend execution methods simulating hospital endpoints defined in openapi.yaml.
"""
from typing import List, Dict, Any, Optional
import uuid

# Mock Database Store
DOCTORS_DB = [
    {
        "id": "DOC-101",
        "name": "Dr. Sarah Jenkins",
        "department": "Dermatology",
        "experience_years": 12,
        "rating": 4.9,
        "bio": "Specialist in skin conditions, acne, eczema, and mole evaluations."
    },
    {
        "id": "DOC-102",
        "name": "Dr. Marcus Vance",
        "department": "Cardiology",
        "experience_years": 18,
        "rating": 4.8,
        "bio": "Expert in cardiovascular health, ECG evaluations, and hypertension management."
    },
    {
        "id": "DOC-103",
        "name": "Dr. Elena Rostova",
        "department": "Neurology",
        "experience_years": 15,
        "rating": 4.9,
        "bio": "Specializes in migraines, neurological assessments, and brain health."
    },
    {
        "id": "DOC-105",
        "name": "Dr. Robert Sterling",
        "department": "Orthopedics",
        "experience_years": 20,
        "rating": 4.8,
        "bio": "Orthopedic surgeon specializing in joint care, bone health, and sports injuries."
    },
    {
        "id": "DOC-106",
        "name": "Dr. David Miller",
        "department": "General Physician",
        "experience_years": 14,
        "rating": 4.9,
        "bio": "General physician providing primary care, routine consultations, fever care, and health checkups."
    },
    {
        "id": "DOC-107",
        "name": "Dr. Priya Sharma",
        "department": "General Physician",
        "experience_years": 11,
        "rating": 4.8,
        "bio": "Primary care physician specializing in internal medicine, health screenings, and preventive care."
    }
]

DEPARTMENTS_DB = [
    {
        "name": "General Physician",
        "description": "Primary healthcare, routine consultations, general health checkups, and wellness.",
        "location": "Building A, Floor 1",
        "contact_ext": "101"
    },
    {
        "name": "Dermatology",
        "description": "Diagnosis and treatment of skin, hair, and nail conditions.",
        "location": "Building A, Floor 2",
        "contact_ext": "201"
    },
    {
        "name": "Cardiology",
        "description": "Heart care, blood pressure management, and ECG diagnostics.",
        "location": "Building B, Floor 1",
        "contact_ext": "104"
    },
    {
        "name": "Neurology",
        "description": "Brain, nerve, and spine disorders management.",
        "location": "Building B, Floor 3",
        "contact_ext": "305"
    },
    {
        "name": "Orthopedics",
        "description": "Bones, joints, muscles, and skeletal system care.",
        "location": "Building A, Floor 3",
        "contact_ext": "309"
    }
]

SLOTS_DB = [
    {"slot_id": "SLOT-001", "doctor_id": "DOC-101", "doctor_name": "Dr. Sarah Jenkins", "department": "Dermatology", "date": "2026-09-20", "time": "09:30 AM", "available": True},
    {"slot_id": "SLOT-002", "doctor_id": "DOC-101", "doctor_name": "Dr. Sarah Jenkins", "department": "Dermatology", "date": "2026-09-20", "time": "11:00 AM", "available": True},
    {"slot_id": "SLOT-003", "doctor_id": "DOC-101", "doctor_name": "Dr. Sarah Jenkins", "department": "Dermatology", "date": "2026-09-21", "time": "02:00 PM", "available": True},
    {"slot_id": "SLOT-004", "doctor_id": "DOC-102", "doctor_name": "Dr. Marcus Vance", "department": "Cardiology", "date": "2026-09-22", "time": "10:00 AM", "available": True},
    {"slot_id": "SLOT-005", "doctor_id": "DOC-102", "doctor_name": "Dr. Marcus Vance", "department": "Cardiology", "date": "2026-09-22", "time": "03:30 PM", "available": True},
    {"slot_id": "SLOT-006", "doctor_id": "DOC-103", "doctor_name": "Dr. Elena Rostova", "department": "Neurology", "date": "2026-09-23", "time": "01:00 PM", "available": True},
    {"slot_id": "SLOT-007", "doctor_id": "DOC-106", "doctor_name": "Dr. David Miller", "department": "General Physician", "date": "2026-09-20", "time": "10:00 AM", "available": True},
    {"slot_id": "SLOT-008", "doctor_id": "DOC-106", "doctor_name": "Dr. David Miller", "department": "General Physician", "date": "2026-09-20", "time": "04:00 PM", "available": True},
    {"slot_id": "SLOT-009", "doctor_id": "DOC-107", "doctor_name": "Dr. Priya Sharma", "department": "General Physician", "date": "2026-09-21", "time": "09:00 AM", "available": True},
]

APPOINTMENTS_DB = [
    {
        "appointment_id": "APP-9001",
        "patient_id": "PAT-1001",
        "doctor_id": "DOC-101",
        "doctor_name": "Dr. Sarah Jenkins",
        "department": "Dermatology",
        "date": "2026-08-12",
        "time": "10:00 AM",
        "status": "completed",
        "notes": "Follow-up for eczema treatment checkup."
    }
]

DOCUMENTS_DB = [
    {
        "doc_id": "DOC-FILE-1",
        "patient_id": "PAT-1001",
        "doc_type": "prescription",
        "title": "Dermatology Prescription - Aug 2026",
        "upload_date": "2026-08-12",
        "content": "Rx: Hydrocortisone Cream 1% - Apply twice daily for 7 days. Cetirizine 10mg - Take 1 tablet nightly for itching.",
        "quality_score": 0.98
    },
    {
        "doc_id": "DOC-FILE-2",
        "patient_id": "PAT-1001",
        "doc_type": "lab_report",
        "title": "Blood Test & IgE Panel",
        "upload_date": "2026-08-14",
        "content": "Hemoglobin: 14.2 g/dL (Normal). Serum IgE: 180 IU/mL (Slightly Elevated - indicative of mild allergy). Allergy Panel: Dust mites (+), Pollen (-).",
        "quality_score": 0.95
    },
    {
        "doc_id": "DOC-FILE-3",
        "patient_id": "PAT-1001",
        "doc_type": "discharge_summary",
        "title": "Skin Clinic OPD Summary",
        "upload_date": "2026-08-12",
        "content": "Patient evaluated for localized contact dermatitis on left arm. Prescribed topical steroid cream and advised patch test if rash recurs.",
        "quality_score": 0.90
    }
]

PATIENTS_DB = {
    "PAT-1001": {
        "patient_id": "PAT-1001",
        "name": "Alex Taylor",
        "age": 34,
        "gender": "Non-binary",
        "allergies": ["Dust mites", "Penicillin"],
        "medical_history_summary": [
            "2024: Mild seasonal allergic rhinitis.",
            "Aug 2026: Contact dermatitis evaluation at Dermatology OPD."
        ]
    }
}

class HospitalAPIBackend:
    """Mock Hospital API Service Class handling queries and mutations."""

    @staticmethod
    def search_doctors(department: Optional[str] = None, query: Optional[str] = None) -> List[Dict[str, Any]]:
        results = DOCTORS_DB
        if department:
            results = [d for d in results if department.lower() in d["department"].lower()]
        if query:
            q = query.lower()
            results = [d for d in results if q in d["name"].lower() or q in d["bio"].lower() or q in d["department"].lower()]
        return results

    @staticmethod
    def get_doctor_by_id(doctor_id: str) -> Optional[Dict[str, Any]]:
        return next((d for d in DOCTORS_DB if d["id"] == doctor_id), None)

    @staticmethod
    def get_departments() -> List[Dict[str, Any]]:
        return DEPARTMENTS_DB

    @staticmethod
    def get_available_slots(doctor_id: Optional[str] = None, department: Optional[str] = None, date: Optional[str] = None) -> List[Dict[str, Any]]:
        results = [s for s in SLOTS_DB if s["available"]]
        if doctor_id:
            results = [s for s in results if s["doctor_id"] == doctor_id]
        if department:
            results = [s for s in results if department.lower() in s["department"].lower()]
        if date:
            results = [s for s in results if s["date"] == date]
        return results

    @staticmethod
    def book_appointment(patient_id: str, doctor_id: str, slot_id: str, notes: Optional[str] = "") -> Dict[str, Any]:
        slot = next((s for s in SLOTS_DB if s["slot_id"] == slot_id), None)
        if not slot or not slot["available"]:
            return {"error": "Slot not available or invalid slot ID."}
        
        doc = next((d for d in DOCTORS_DB if d["id"] == doctor_id), None)
        if not doc:
            return {"error": "Doctor not found."}

        slot["available"] = False
        new_app = {
            "appointment_id": f"APP-{uuid.uuid4().hex[:6].upper()}",
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "doctor_name": doc["name"],
            "department": doc["department"],
            "date": slot["date"],
            "time": slot["time"],
            "status": "confirmed",
            "notes": notes or "Booked via Smart Hospital Assistant"
        }
        APPOINTMENTS_DB.append(new_app)
        return {"success": True, "appointment": new_app}

    @staticmethod
    def cancel_appointment(appointment_id: str) -> Dict[str, Any]:
        app = next((a for a in APPOINTMENTS_DB if a["appointment_id"] == appointment_id), None)
        if not app:
            return {"error": "Appointment ID not found."}
        
        app["status"] = "cancelled"
        for s in SLOTS_DB:
            if s["doctor_name"] == app["doctor_name"] and s["date"] == app["date"] and s["time"] == app["time"]:
                s["available"] = True

        return {"success": True, "cancelled_appointment_id": appointment_id}

    @staticmethod
    def get_appointment_history(patient_id: str) -> List[Dict[str, Any]]:
        return [a for a in APPOINTMENTS_DB if a["patient_id"] == patient_id]

    @staticmethod
    def get_patient_documents(patient_id: str) -> List[Dict[str, Any]]:
        return [d for d in DOCUMENTS_DB if d["patient_id"] == patient_id]

    @staticmethod
    def get_patient_record(patient_id: str) -> Dict[str, Any]:
        return PATIENTS_DB.get(patient_id, {"error": "Patient record not found"})
