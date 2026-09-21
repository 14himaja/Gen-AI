from typing import Annotated
import uuid
from fastapi import APIRouter, Depends, HTTPException
from google.genai import types

from app.api.auth import get_current_user
from app.agents.root_agent import runner
from app.models import User, ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["Conversational AI Assistant"])


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

    final_reply = "".join(replies).strip() or "I have processed your request."

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

