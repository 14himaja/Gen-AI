import asyncio
from app.agents.root_agent import runner
from google.genai import types

async def test_query(prompt, session_id):
    user_id = "P1002"
    session = await runner.session_service.get_session(
        app_name="smart_hospital",
        user_id=user_id,
        session_id=session_id
    )
    if not session:
        session = await runner.session_service.create_session(
            app_name="smart_hospital",
            user_id=user_id,
            session_id=session_id,
            state={"user_id": user_id, "user_name": "Priya Patel", "user_role": "PATIENT"}
        )

    content = types.Content(parts=[types.Part.from_text(text=prompt)])
    
    replies = []
    active_agent = "hospital_root_agent"

    print(f"\n--- PROMPT: {prompt} ---")
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        if hasattr(event, "author") and event.author:
            active_agent = event.author
        if hasattr(event, "content") and event.content:
            for part in getattr(event.content, "parts", []):
                text = getattr(part, 'text', None)
                fc = getattr(part, 'function_call', None)
                fr = getattr(part, 'function_response', None)
                print(f"[{active_agent}] text={repr(text)}, fc={fc.name if fc else None}, fr={fr.name if fr else None}")
                if text:
                    replies.append(text)

    final_reply = "".join(replies).strip()
    print(f"FINAL RESULT ({active_agent}): {repr(final_reply)}")

async def main():
    await test_query("What departments are available?", "sess-test-101")
    await test_query("What are your hospital hours?", "sess-test-102")

if __name__ == "__main__":
    asyncio.run(main())
