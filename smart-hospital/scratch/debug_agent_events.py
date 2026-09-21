import asyncio
import os
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.models.lite_llm import LiteLlm
from google.genai import types

os.environ["OPENROUTER_API_KEY"] = "sk-or-v1-dummykey123"

def search_departments():
    """Lists available hospital departments."""
    return {
        "status": "success",
        "departments": [
            {"id": "DEP-DERM", "name": "Dermatology", "description": "Skin and hair care."},
            {"id": "DEP-CARD", "name": "Cardiology", "description": "Heart care."}
        ]
    }

async def test_model(model_name):
    print(f"\n================ TESTING MODEL: {model_name} ================")
    llm = LiteLlm(model=model_name, api_key="sk-or-v1-dummykey123")
    test_agent = Agent(
        model=llm,
        name="test_info_agent",
        description="Info agent",
        instruction="Answer user questions using tools. Return clear factual answers with the department names.",
        tools=[search_departments]
    )
    session_service = InMemorySessionService()
    runner = Runner(agent=test_agent, session_service=session_service, app_name="test_app", auto_create_session=True)
    
    content = types.Content(parts=[types.Part.from_text(text='What departments are available?')])
    replies = []
    try:
        async for event in runner.run_async(user_id='P1001', session_id='SESS-1', new_message=content):
            content_obj = getattr(event, 'content', None)
            if content_obj and hasattr(content_obj, 'parts'):
                for part in content_obj.parts:
                    t = getattr(part, 'text', None)
                    fc = getattr(part, 'function_call', None)
                    if t:
                        print(f"  --> TEXT: {t}")
                        replies.append(t)
                    if fc:
                        print(f"  --> CALL: {fc.name}")
        print(">>> FINAL REPLIES:", replies)
    except Exception as e:
        print(f"ERROR: {e}")

async def main():
    models_to_test = [
        "openrouter/google/gemini-flash-1.5",
        "openrouter/meta-llama/llama-3.3-70b-instruct",
        "openrouter/qwen/qwen-2.5-7b-instruct",
        "openrouter/mistralai/mistral-small-24b-instruct-2501"
    ]
    for m in models_to_test:
        await test_model(m)

if __name__ == '__main__':
    asyncio.run(main())
