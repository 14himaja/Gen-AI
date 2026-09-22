from typing import Annotated, List, Optional
import uuid
import base64
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from google.genai import types

from app.api.auth import get_current_user
from app.agents.root_agent import runner
from app.agents.tools import book_appointment, cancel_appointment, reschedule_appointment
from app.models import User, ChatRequest, ChatResponse, DocumentType
from app.database import db
from app.api.admin import extract_text_from_file

router = APIRouter(prefix="/chat", tags=["Conversational AI Assistant"])


def extract_text_from_upload(file_bytes: bytes, filename: str) -> str:
    """Extract text from uploaded image or PDF/TXT document."""
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    
    # If image file (PNG, JPG, JPEG, WEBP, GIF), attempt OCR / text extraction via PIL & fitz or LLM vision
    if ext in ("png", "jpg", "jpeg", "webp", "bmp", "gif"):
        try:
            import fitz
            doc = fitz.open(stream=file_bytes, filetype=ext)
            text_parts = [page.get_text("text").strip() for page in doc if page.get_text("text").strip()]
            if text_parts:
                return "\n".join(text_parts)
        except Exception:
            pass

        try:
            from litellm import completion
            from app.config import settings
            cfg = settings.get_llm_config()
            
            b64_img = base64.b64encode(file_bytes).decode('utf-8')
            mime_type = f"image/{'jpeg' if ext in ('jpg', 'jpeg') else ext}"
            data_url = f"data:{mime_type};base64,{b64_img}"
            
            # Select vision-capable model
            vision_model = cfg["model_name"]
            if "llama-3.3" in vision_model or "instruct" in vision_model and "vision" not in vision_model:
                if cfg.get("provider") == "openrouter":
                    vision_model = "openrouter/google/gemini-2.5-flash"
                else:
                    vision_model = "gemini/gemini-2.5-flash"

            resp = completion(
                model=vision_model,
                api_key=cfg.get("api_key"),
                api_base=cfg.get("api_base"),
                max_tokens=1000,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract and transcribe all text, medications, dosage, instructions, doctor details, and clinical notes from this prescription or medical document photo. Be thorough and accurate."},
                        {"type": "image_url", "image_url": {"url": data_url}}
                    ]
                }]
            )
            extracted = resp.choices[0].message.content
            if extracted and len(extracted.strip()) > 10:
                return extracted.strip()
        except Exception as e:
            print("Vision extraction error:", e)

    # Fallback to standard PDF/TXT document text extraction
    txt = extract_text_from_file(file_bytes, filename)
    if txt and txt.strip():
        return txt.strip()
    return f"[Uploaded Document File: {filename}]"


@router.post("", response_model=ChatResponse)
async def chat_with_assistant(
    payload: ChatRequest,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Conversational endpoint invoking Google ADK Root Agent with authenticated identity context."""
    session_id = payload.session_id or f"SESS-{current_user.user_id}-{uuid.uuid4().hex[:6]}"

    # Retrieve or create ADK session
    session = await runner.session_service.get_session(
        app_name="smart_hospital",
        user_id=current_user.user_id,
        session_id=session_id
    )

    initial_state = {
        "user_id": current_user.user_id,
        "user_name": current_user.name,
        "user_role": current_user.role.value
    }

    if not session:
        session = await runner.session_service.create_session(
            app_name="smart_hospital",
            user_id=current_user.user_id,
            session_id=session_id,
            state=initial_state
        )
    else:
        # Guarantee state is synchronized with authenticated identity
        session.state.update(initial_state)

    # Reset turn tracking state
    session.state["turn_tools_used"] = []
    session.state["turn_retrieved_chunks"] = []

    # Check for pending action confirmation (e.g. user saying "yes" to book appointment)
    msg_clean = payload.message.strip().lower()
    is_confirmation = msg_clean in ("yes", "y", "confirm", "yes, confirm", "yes please", "sure", "yeah", "confirmed", "proceed", "go ahead") or msg_clean.startswith("yes") or msg_clean.startswith("confirm")

    pending_action = session.state.get("pending_action")
    if is_confirmation and pending_action and isinstance(pending_action, dict):
        action_name = pending_action.get("action")
        if action_name == "book_appointment":
            doc_id = pending_action.get("doctor_id")
            date_str = pending_action.get("date")
            time_str = pending_action.get("time")
            notes = pending_action.get("notes", "")

            res = book_appointment(user_id=current_user.user_id, doctor_id=doc_id, date=date_str, time=time_str, confirmed=True, notes=notes)
            session.state.pop("pending_action", None)

            if res.get("status") == "success":
                appt_details = res.get("details", {})
                final_reply = (
                    f"✅ **Appointment Successfully Booked!**\n\n"
                    f"- **Appointment ID:** `{res.get('appointment_id')}`\n"
                    f"- **Doctor:** {appt_details.get('doctor')}\n"
                    f"- **Department:** {appt_details.get('department')}\n"
                    f"- **Date:** {appt_details.get('date')}\n"
                    f"- **Time:** {appt_details.get('time')}\n"
                    f"- **Status:** {appt_details.get('status')}\n\n"
                    f"Your appointment has been saved to your account history and synced with the hospital ledger."
                )
                return ChatResponse(
                    session_id=session_id,
                    reply=final_reply,
                    active_agent="appointment_agent",
                    state=dict(session.state),
                    source_type="tool",
                    llm_used=True,
                    rag_used=False,
                    tools_used=["book_appointment"],
                    retrieved_chunks=[],
                    trace_id=f"TRACE-{uuid.uuid4().hex[:8]}"
                )

    # Format message for Google ADK
    content = types.Content(
        parts=[types.Part.from_text(text=payload.message)]
    )

    replies = []
    active_agent = "hospital_root_agent"

    try:
        async for event in runner.run_async(
            user_id=current_user.user_id,
            session_id=session_id,
            new_message=content
        ):
            # Inspect event author
            if hasattr(event, "author") and event.author:
                active_agent = event.author

            # Extract generated response text
            if hasattr(event, "content") and event.content:
                for part in getattr(event.content, "parts", []):
                    if hasattr(part, "text") and part.text:
                        replies.append(part.text)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Agent execution encountered an error: {str(e)}"
        )

    raw_reply = "".join(replies).strip()
    if not raw_reply:
        msg_lower = payload.message.lower().strip()
        if any(g in msg_lower for g in ("hi", "hello", "hey", "good morning", "good afternoon", "good evening", "greetings")):
            final_reply = "Hello! Welcome to ApolloCare. How can I assist you with your appointments, doctors, or medical documents today?"
        else:
            final_reply = "I am here to assist you with your appointments, medical records, and hospital information. How can I help you today?"
    else:
        final_reply = raw_reply

    # Extract telemetry metrics
    tools_used = session.state.get("turn_tools_used", [])
    retrieved_chunks = session.state.get("turn_retrieved_chunks", [])
    rag_used = "search_hospital_knowledge" in tools_used or len(retrieved_chunks) > 0

    if rag_used:
        source_type = "llm_rag"
    elif tools_used:
        source_type = "tool"
    else:
        source_type = "llm"

    trace_id = f"TRACE-{uuid.uuid4().hex[:8]}"

    return ChatResponse(
        session_id=session_id,
        reply=final_reply,
        active_agent=active_agent,
        state=dict(session.state),
        source_type=source_type,
        llm_used=True,
        rag_used=rag_used,
        tools_used=tools_used,
        retrieved_chunks=retrieved_chunks,
        trace_id=trace_id
    )


@router.post("/upload", response_model=ChatResponse)
async def chat_with_file_upload(
    current_user: Annotated[User, Depends(get_current_user)],
    message: str = Form(""),
    patient_id: Optional[str] = Form(None),
    session_id: Optional[str] = Form(None),
    files: List[UploadFile] = File(...)
):
    """Handle document/prescription file uploads in chat, extract text via OCR, save to history, and ask agent."""
    effective_session_id = session_id or f"SESS-{current_user.user_id}-{uuid.uuid4().hex[:6]}"

    extracted_attachments = []

    for file in files:
        file_bytes = await file.read()
        extracted_text = extract_text_from_upload(file_bytes, file.filename)

        # Determine document type (Prescription vs General Medical Document)
        fname_lower = file.filename.lower()
        if any(k in fname_lower or k in extracted_text.lower() for k in ("rx", "prescription", "medicine", "dosage", "tablet", "capsule", "pharma", "doctor")):
            doc_type = DocumentType.PRESCRIPTION
        else:
            doc_type = DocumentType.LAB_REPORT

        # Save extracted document to patient database record for long-term agent memory
        doc_record = db.add_document(
            user_id=current_user.user_id,
            title=file.filename,
            doc_type=doc_type,
            extracted_text=extracted_text
        )

        extracted_attachments.append(
            f"📄 **Attachment Saved:** `{file.filename}` (Type: {doc_type.value})\n"
            f"**Extracted Document / Prescription Details:**\n{extracted_text}"
        )

    attachment_prompt = "\n\n".join(extracted_attachments)
    user_prompt = f"{attachment_prompt}\n\nUser Question: {message}" if message.strip() else f"{attachment_prompt}\n\nPlease summarize and explain what is written in this uploaded document/prescription."

    # Invoke standard assistant logic with the enhanced text prompt
    req = ChatRequest(message=user_prompt, session_id=effective_session_id)
    return await chat_with_assistant(payload=req, current_user=current_user)
