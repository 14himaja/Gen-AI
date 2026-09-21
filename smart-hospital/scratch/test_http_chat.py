from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_api_chat():
    login_res = client.post("/api/auth/login", json={"email": "priya@example.com", "password": "password123"})
    print("LOGIN STATUS:", login_res.status_code)
    token = login_res.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Ask "What departments are available?"
    res1 = client.post("/api/chat", headers=headers, json={
        "message": "What departments are available?",
        "patient_id": "P1002",
        "session_id": "test-http-session-1"
    })
    print("\n--- RESPONSE 1 ('What departments are available?') ---")
    print("Status:", res1.status_code)
    print("Reply:", repr(res1.json().get("reply")))
    print("Active Agent:", res1.json().get("active_agent"))

    # 2. Ask "What are your hospital hours?"
    res2 = client.post("/api/chat", headers=headers, json={
        "message": "What are your hospital hours?",
        "patient_id": "P1002",
        "session_id": "test-http-session-1"
    })
    print("\n--- RESPONSE 2 ('What are your hospital hours?') ---")
    print("Status:", res2.status_code)
    print("Reply:", repr(res2.json().get("reply")))
    print("Active Agent:", res2.json().get("active_agent"))

if __name__ == "__main__":
    test_api_chat()
