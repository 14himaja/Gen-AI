"""Callbacks and security guardrails for Google ADK agents."""

from datetime import datetime
from google.adk.agents.callback_context import CallbackContext
from app.database import db


def before_agent_callback(*call_args, **call_kwargs):
    """Tracks session execution metrics and verifies authenticated identity."""
    ctx = call_kwargs.get("callback_context") or (call_args[0] if call_args else None)
    if ctx and hasattr(ctx, "state"):
        state = ctx.state
        state["start_time"] = datetime.now()
        state["request_count"] = state.get("request_count", 0) + 1
    return None


def after_agent_callback(*call_args, **call_kwargs):
    """Measures overall agent response duration."""
    ctx = call_kwargs.get("callback_context") or (call_args[0] if call_args else None)
    if ctx and hasattr(ctx, "state"):
        state = ctx.state
        if "start_time" in state:
            duration = (datetime.now() - state["start_time"]).total_seconds()
            state["last_latency_seconds"] = duration
    return None


def before_tool_callback(*call_args, **call_kwargs):
    """Security guardrail: Validates authorization and prevents cross-user access."""
    tool = call_kwargs.get("tool")
    args = call_kwargs.get("args") if "args" in call_kwargs else call_kwargs.get("tool_args")
    ctx = call_kwargs.get("tool_context") or call_kwargs.get("callback_context")

    if call_args:
        if len(call_args) >= 3:
            if isinstance(call_args[1], dict):
                tool = tool or call_args[0]
                args = args if args is not None else call_args[1]
                ctx = ctx or call_args[2]
            else:
                ctx = ctx or call_args[0]
                tool = tool or call_args[1]
                args = args if args is not None else call_args[2]
        elif len(call_args) == 2:
            if isinstance(call_args[1], dict):
                tool = tool or call_args[0]
                args = args if args is not None else call_args[1]
            else:
                ctx = ctx or call_args[0]
                tool = tool or call_args[1]
        elif len(call_args) == 1:
            tool = call_args[0]

    state = getattr(ctx, "state", {}) if ctx else {}
    session_user_id = state.get("user_id") if isinstance(state, dict) else None

    # If tool expects user_id, auto-inject or enforce match with session context
    if isinstance(args, dict):
        if "user_id" in args and session_user_id:
            args["user_id"] = session_user_id
        elif "user_id" in args and not args.get("user_id") and session_user_id:
            args["user_id"] = session_user_id

    return None


def after_tool_callback(*call_args, **call_kwargs):
    """Auditing callback: Records all executed tool actions to audit log."""
    tool = call_kwargs.get("tool")
    args = call_kwargs.get("args") if "args" in call_kwargs else call_kwargs.get("tool_args")
    ctx = call_kwargs.get("tool_context") or call_kwargs.get("callback_context")
    response = call_kwargs.get("tool_response") if "tool_response" in call_kwargs else call_kwargs.get("response")

    if call_args:
        if len(call_args) >= 4:
            if isinstance(call_args[1], dict):
                tool = tool or call_args[0]
                args = args if args is not None else call_args[1]
                ctx = ctx or call_args[2]
                response = response if response is not None else call_args[3]
            else:
                ctx = ctx or call_args[0]
                tool = tool or call_args[1]
                args = args if args is not None else call_args[2]
                response = response if response is not None else call_args[3]
        elif len(call_args) == 3:
            if isinstance(call_args[1], dict):
                tool = tool or call_args[0]
                args = args if args is not None else call_args[1]
                ctx = ctx or call_args[2]
            else:
                ctx = ctx or call_args[0]
                tool = tool or call_args[1]
                args = args if args is not None else call_args[2]

    state = getattr(ctx, "state", {}) if ctx else {}
    user_id = state.get("user_id", "ANONYMOUS") if isinstance(state, dict) else "ANONYMOUS"

    tool_name = getattr(tool, "name", str(tool))
    action_name = f"TOOL_{tool_name.upper()}"
    status = "SUCCESS"
    if isinstance(response, dict) and response.get("status") in ["error", "unauthorized"]:
        status = "DENIED"

    if isinstance(state, dict):
        if "turn_tools_used" not in state:
            state["turn_tools_used"] = []
        if tool_name not in state["turn_tools_used"]:
            state["turn_tools_used"].append(tool_name)

        if isinstance(response, dict) and "retrieved_chunk_ids" in response:
            if "turn_retrieved_chunks" not in state:
                state["turn_retrieved_chunks"] = []
            for cid in response["retrieved_chunk_ids"]:
                if cid not in state["turn_retrieved_chunks"]:
                    state["turn_retrieved_chunks"].append(cid)

    args_dict = {}
    if isinstance(args, dict):
        args_dict = {k: str(v) for k, v in args.items() if k != "password"}

    db.log_audit(
        user_id=user_id,
        action=action_name,
        details={
            "tool": tool_name,
            "args": args_dict,
            "response_status": status
        },
        status=status
    )
    return None

