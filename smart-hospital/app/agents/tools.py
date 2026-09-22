"""Deterministic tool functions for Google ADK agents."""

from typing import Dict, Any, List
from app.database import db


def search_departments() -> Dict[str, Any]:
    """Retrieve the list of all hospital departments and their locations."""
    depts = db.get_departments()
    return {
        "status": "success",
        "count": len(depts),
        "departments": [
            {
                "id": d.id,
                "name": d.name,
                "description": d.description,
                "location": d.location
            }
            for d in depts
        ]
    }


def search_doctors(department_name: str = "", specialty: str = "") -> Dict[str, Any]:
    """Search for doctors by department name or specialty."""
    docs = db.get_doctors(department_name=department_name or None, specialty=specialty or None)
    return {
        "status": "success",
        "count": len(docs),
        "doctors": [
            {
                "id": d.id,
                "name": d.name,
                "department": d.department_name,
                "specialty": d.specialty,
                "available_days": d.available_days,
                "fee": f"${d.consultation_fee:.2f}"
            }
            for d in docs
        ]
    }


def get_available_slots(doctor_id: str, date: str) -> Dict[str, Any]:
    """Get available appointment time slots for a given doctor on a specific date (YYYY-MM-DD)."""
    doc = db.get_doctor(doctor_id)
    actual_doc_id = doc.id if doc else doctor_id
    slots = db.get_slots(doctor_id=actual_doc_id, date_str=date)
    return {
        "status": "success",
        "doctor_id": actual_doc_id,
        "doctor_name": doc.name if doc else doctor_id,
        "date": date,
        "available_slots": [s.time for s in slots]
    }


def book_appointment(user_id: str, doctor_id: str, date: str, time: str, confirmed: bool = False, notes: str = "") -> Dict[str, Any]:
    """Book an appointment for a patient.
    
    CRITICAL GUARDRAIL: The user must explicitly confirm the booking details before calling this tool with confirmed=True.
    If confirmed is False, return a confirmation prompt request.
    """
    doc = db.get_doctor(doctor_id)
    doc_name = doc.name if doc else doctor_id
    actual_doc_id = doc.id if doc else doctor_id

    if not confirmed:
        return {
            "status": "confirmation_required",
            "message": (
                f"Please confirm: Do you want to book an appointment with {doc_name} "
                f"on {date} at {time}? Respond 'Yes, I confirm' to proceed."
            ),
            "pending_action": {
                "action": "book_appointment",
                "doctor_id": actual_doc_id,
                "doctor_name": doc_name,
                "date": date,
                "time": time,
                "notes": notes
            }
        }

    appt = db.book_appointment(user_id=user_id, doctor_id=actual_doc_id, date_str=date, time_str=time, notes=notes)
    if not appt:
        return {
            "status": "error",
            "message": "Doctor or slot not found. Please choose another time."
        }

    return {
        "status": "success",
        "message": f"Appointment successfully booked with {appt.doctor_name} for {appt.date} at {appt.time}.",
        "appointment_id": appt.id,
        "details": {
            "doctor": appt.doctor_name,
            "department": appt.department_name,
            "date": appt.date,
            "time": appt.time,
            "status": appt.status.value
        }
    }


def cancel_appointment(user_id: str, appointment_id: str, confirmed: bool = False) -> Dict[str, Any]:
    """Cancel an existing appointment.
    
    CRITICAL GUARDRAIL: The user must explicitly confirm cancellation before confirmed=True is passed.
    """
    appt = db.appointments.get(appointment_id)
    if not appt or appt.user_id != user_id:
        return {
            "status": "error",
            "message": "Appointment not found or you are not authorized to cancel it."
        }

    if not confirmed:
        return {
            "status": "confirmation_required",
            "message": (
                f"Are you sure you want to cancel your appointment with {appt.doctor_name} "
                f"on {appt.date} at {appt.time}? Respond 'Confirm cancellation' to proceed."
            ),
            "pending_action": {
                "action": "cancel_appointment",
                "appointment_id": appointment_id
            }
        }

    success = db.cancel_appointment(user_id=user_id, appointment_id=appointment_id)
    if success:
        return {
            "status": "success",
            "message": f"Appointment {appointment_id} has been cancelled."
        }
    return {
        "status": "error",
        "message": "Failed to cancel appointment."
    }


def reschedule_appointment(user_id: str, appointment_id: str, new_date: str, new_time: str, confirmed: bool = False) -> Dict[str, Any]:
    """Reschedule an existing appointment to a new date and time.
    
    CRITICAL GUARDRAIL: User confirmation required before confirmed=True.
    """
    appt = db.appointments.get(appointment_id)
    if not appt or appt.user_id != user_id:
        return {
            "status": "error",
            "message": "Appointment not found or you are not authorized to reschedule it."
        }

    if not confirmed:
        return {
            "status": "confirmation_required",
            "message": (
                f"Please confirm: Reschedule appointment {appointment_id} with {appt.doctor_name} "
                f"to {new_date} at {new_time}? Respond 'Yes, confirm reschedule' to proceed."
            ),
            "pending_action": {
                "action": "reschedule_appointment",
                "appointment_id": appointment_id,
                "new_date": new_date,
                "new_time": new_time
            }
        }

    rescheduled = db.reschedule_appointment(user_id=user_id, appointment_id=appointment_id, new_date=new_date, new_time=new_time)
    if rescheduled:
        return {
            "status": "success",
            "message": f"Appointment {appointment_id} rescheduled to {new_date} at {new_time}.",
            "appointment": {
                "id": rescheduled.id,
                "doctor": rescheduled.doctor_name,
                "date": rescheduled.date,
                "time": rescheduled.time
            }
        }
    return {
        "status": "error",
        "message": "Could not reschedule appointment."
    }


def get_appointment_history(user_id: str) -> Dict[str, Any]:
    """Retrieve appointment history strictly for the authenticated user."""
    appts = db.get_user_appointments(user_id=user_id)
    return {
        "status": "success",
        "user_id": user_id,
        "total_appointments": len(appts),
        "appointments": [
            {
                "id": a.id,
                "doctor": a.doctor_name,
                "department": a.department_name,
                "date": a.date,
                "time": a.time,
                "status": a.status.value,
                "notes": a.notes
            }
            for a in sorted(appts, key=lambda x: x.date, reverse=True)
        ]
    }


def get_patient_documents(user_id: str) -> Dict[str, Any]:
    """List medical documents belonging to the authenticated user."""
    docs = db.get_user_documents(user_id=user_id)
    return {
        "status": "success",
        "user_id": user_id,
        "count": len(docs),
        "documents": [
            {
                "id": d.id,
                "title": d.title,
                "type": d.document_type.value,
                "upload_date": d.upload_date,
                "summary": d.summary
            }
            for d in docs
        ]
    }


def read_document(user_id: str, document_id: str) -> Dict[str, Any]:
    """Read the extracted contents of an authorized document."""
    doc = db.documents.get(document_id)
    if not doc or doc.user_id != user_id:
        return {
            "status": "error",
            "message": "Document not found or unauthorized access."
        }

    return {
        "status": "success",
        "document_id": doc.id,
        "title": doc.title,
        "type": doc.document_type.value,
        "content": doc.extracted_text,
        "summary": doc.summary,
        "key_findings": doc.key_findings
    }


def search_hospital_knowledge(query: str) -> Dict[str, Any]:
    """Search hospital general information, policies, visiting hours, and registration FAQs."""
    results = db.search_knowledge_base(query=query)
    chunk_ids = [r["chunk_id"] for r in results if "chunk_id" in r]
    return {
        "status": "success",
        "query": query,
        "knowledge_entries": results,
        "retrieved_chunk_ids": chunk_ids
    }



def prepare_consultation_summary(user_id: str) -> Dict[str, Any]:
    """Aggregate authorized patient history and documents into a structured consultation preparation brief."""
    appts = db.get_user_appointments(user_id=user_id)
    docs = db.get_user_documents(user_id=user_id)
    user = db.get_user(user_id)

    # Resolve patient name from user record, or fall back to appointment records
    patient_name = None
    if user and user.name:
        patient_name = user.name
    elif appts:
        # Some seeded appointments store the patient name indirectly; use user_id as fallback
        patient_name = None
    patient_name = patient_name or (f"Patient {user_id}" if user_id else "Patient")

    recent_appts = sorted(appts, key=lambda x: x.date, reverse=True)[:3]
    recent_docs = sorted(docs, key=lambda x: x.upload_date, reverse=True)[:3]

    return {
        "status": "success",
        "patient_id": user_id,
        "patient_name": patient_name,
        "summary_brief": {
            "total_past_appointments": len(appts),
            "recent_appointments": [
                f"{a.date} - {a.doctor_name} ({a.department_name}) [{a.status.value}]"
                for a in recent_appts
            ] if recent_appts else ["No past appointments found."],
            "relevant_documents": [
                f"{d.title} ({d.document_type.value}) uploaded on {d.upload_date}: {d.summary or 'Document on file'}"
                for d in recent_docs
            ] if recent_docs else ["No medical documents uploaded yet."]
        }
    }
