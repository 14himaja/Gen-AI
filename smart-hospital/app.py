"""
AI Smart Hospital Assistant - Web Dashboard & API Server.
Built with FastAPI & Modern Glassmorphism Vanilla CSS/JS UI.
Demonstrates all 13 Google ADK concepts interactively in the browser.
"""
from fastapi import FastAPI, Request, Body, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from api.mock_server import HospitalAPIBackend
from mcp.server import mcp_server_instance
from tools.hospital_tools import search_doctors, get_available_slots, book_appointment, cancel_appointment, read_document
from agents.doctor_rec_agent import recommend_doctor_tool
from workflows.sequential_workflow import run_sequential_workflow
from workflows.parallel_workflow import run_parallel_workflow
from workflows.loop_workflow import run_document_quality_loop
from state_memory.session_state import session_state_manager
from state_memory.long_term_memory import memory_store_instance
from callbacks.security import (
    before_model_pii_redaction_callback,
    before_tool_action_confirmation_callback,
    enforce_medical_non_diagnosis_guardrail
)

app = FastAPI(
    title="AI Smart Hospital Assistant",
    description="Operations Assistant powered by Google ADK (Agent Development Kit)",
    version="1.0.0"
)

@app.get("/api/doctors")
def api_get_doctors(department: str = None, query: str = None):
    return HospitalAPIBackend.search_doctors(department=department, query=query)

@app.get("/api/departments")
def api_get_departments():
    return HospitalAPIBackend.get_departments()

@app.get("/api/slots")
def api_get_slots(department: str = None, doctor_id: str = None):
    return HospitalAPIBackend.get_available_slots(department=department, doctor_id=doctor_id)

@app.post("/api/book")
def api_book_appointment(payload: dict = Body(...)):
    patient_id = payload.get("patient_id", "PAT-1001")
    doctor_id = payload.get("doctor_id")
    slot_id = payload.get("slot_id")
    user_confirmed = payload.get("confirmed", True)

    # Tool Callback Validation
    conf_check = before_tool_action_confirmation_callback("book_appointment", payload, user_confirmed)
    if conf_check["blocked"]:
        return JSONResponse(status_code=400, content=conf_check)

    return HospitalAPIBackend.book_appointment(patient_id, doctor_id, slot_id, payload.get("notes", ""))

@app.post("/api/cancel")
def api_cancel_appointment(payload: dict = Body(...)):
    appointment_id = payload.get("appointment_id")
    user_confirmed = payload.get("confirmed", False)

    # Action Confirmation Guardrail Callback
    conf_check = before_tool_action_confirmation_callback("cancel_appointment", payload, user_confirmed)
    if conf_check["blocked"]:
        return JSONResponse(status_code=400, content=conf_check)

    return HospitalAPIBackend.cancel_appointment(appointment_id)

@app.post("/api/chat")
def api_chat(payload: dict = Body(...)):
    user_msg = payload.get("message", "")
    session_id = payload.get("session_id", "SESSION-001")
    patient_id = payload.get("patient_id", "PAT-1001")

    # 1. Apply Model Callback (PII Redaction)
    clean_prompt = before_model_pii_redaction_callback(user_msg)

    # 2. Update Session State
    session = session_state_manager.get_session(session_id)

    # 3. Handle specific operational intents
    msg_lower = clean_prompt.lower()
    
    if "usual appointment" in msg_lower or "usual" in msg_lower:
        context = memory_store_instance.get_usual_appointment_context(patient_id)
        reply = (
            f"🧠 Retrieved your long-term preferences!\n"
            f"• Preferred Hospital: {context['hospital']}\n"
            f"• Department: {context['department']}\n"
            f"• Preferred Doctor: {context['doctor']}\n"
            f"• Preferred Time: {context['preferred_time']}\n\n"
            f"Found open slots for Dr. David Miller. Would you like me to confirm SLOT-007 (2026-09-20 at 10:00 AM)?"
        )
        active_agent = "history_agent -> appointment_agent"
    elif "dermatologist" in msg_lower or "skin" in msg_lower:
        docs = search_doctors(department="Dermatology")
        slots = get_available_slots(department="Dermatology")
        reply = f"Found Dermatology specialist {docs[0]['name']} ({docs[0]['rating']}/5.0). Available slot: {slots[0]['date']} at {slots[0]['time']} ({slots[0]['slot_id']})."
        active_agent = "appointment_agent"
    elif "prescription" in msg_lower or "medicine" in msg_lower:
        doc = read_document("DOC-FILE-1", patient_id)
        reply = (
            f"📄 Extracted Prescription Information ({doc['title']}):\n"
            f"1. Hydrocortisone Cream 1% - Apply twice daily for 7 days.\n"
            f"2. Cetirizine 10mg - Take 1 tablet nightly for itching."
        )
        active_agent = "document_agent"
    elif "ecg" in msg_lower or "cardiology" in msg_lower:
        reply = "Cardiology handles heart care, blood pressure management, and ECG diagnostics. An ECG (electrocardiogram) records the electrical signals in your heart to check for heart conditions."
        active_agent = "information_agent"
    elif "summary" in msg_lower or "doctor summary" in msg_lower:
        seq_res = run_sequential_workflow(patient_id, "DOC-FILE-1")
        reply = f"📊 Generated Doctor Visit Summary Report successfully via Sequential ADK Workflow!\n\n{seq_res['steps'][2]['output']}"
        active_agent = "report_agent (Sequential Workflow)"
    else:
        rec = recommend_doctor_tool(department="General Physician")
        reply = f"Welcome to Smart Hospital! I recommend consulting {rec['recommended_doctor']} ({rec['department']}). How can I assist you with appointments, documents, or hospital info today?"
        active_agent = "hospital_root_manager"

    # 4. Apply Medical Non-Diagnosis Guardrail
    guarded_reply = enforce_medical_non_diagnosis_guardrail(reply)

    return {
        "reply": guarded_reply,
        "active_agent": active_agent,
        "pii_sanitized": clean_prompt != user_msg,
        "session_state": session.dict()
    }

@app.post("/api/workflows/sequential")
def api_sequential_workflow(payload: dict = Body(...)):
    return run_sequential_workflow(payload.get("patient_id", "PAT-1001"), payload.get("doc_id", "DOC-FILE-1"))

@app.post("/api/workflows/parallel")
def api_parallel_workflow(payload: dict = Body(...)):
    return run_parallel_workflow(payload.get("patient_id", "PAT-1001"), payload.get("doc_id", "DOC-FILE-1"))

@app.post("/api/workflows/loop")
def api_loop_workflow(payload: dict = Body(...)):
    return run_document_quality_loop(payload.get("doc_id", "DOC-FILE-1"), payload.get("patient_id", "PAT-1001"))

@app.get("/", response_class=HTMLResponse)
def index_page():
    return HTMLResponse(content="""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏥 AI Smart Hospital Assistant - Google ADK</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #0b0f19;
            --surface: #151c2e;
            --surface-accent: #1e2942;
            --primary: #38bdf8;
            --primary-glow: rgba(56, 189, 248, 0.25);
            --accent: #818cf8;
            --success: #34d399;
            --warning: #fbbf24;
            --danger: #f87171;
            --text: #f8fafc;
            --text-muted: #94a3b8;
            --border: #334155;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Outfit', sans-serif; }
        body { background: var(--bg); color: var(--text); display: flex; height: 100vh; overflow: hidden; }
        
        .sidebar { width: 320px; background: var(--surface); border-right: 1px solid var(--border); padding: 24px; display: flex; flex-direction: column; gap: 20px; overflow-y: auto; }
        .logo-title { display: flex; align-items: center; gap: 12px; font-size: 1.2rem; font-weight: 700; color: var(--primary); }
        
        .badge { background: var(--surface-accent); border: 1px solid var(--border); padding: 6px 12px; border-radius: 20px; font-size: 0.8rem; color: var(--accent); width: fit-content; }
        
        .card { background: var(--surface-accent); border: 1px solid var(--border); border-radius: 12px; padding: 16px; display: flex; flex-direction: column; gap: 10px; }
        .card-title { font-size: 0.9rem; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; }
        
        .btn { background: var(--primary); color: #0f172a; border: none; padding: 10px 16px; border-radius: 8px; font-weight: 600; cursor: pointer; transition: all 0.2s; display: inline-flex; align-items: center; justify-content: center; gap: 8px; }
        .btn:hover { box-shadow: 0 0 15px var(--primary-glow); transform: translateY(-1px); }
        .btn-outline { background: transparent; border: 1px solid var(--primary); color: var(--primary); }
        .btn-outline:hover { background: var(--primary-glow); }
        
        .main-content { flex: 1; display: flex; flex-direction: column; height: 100vh; background: radial-gradient(circle at top right, rgba(56, 189, 248, 0.05), transparent 40%); }
        
        .top-nav { height: 64px; border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; padding: 0 32px; background: var(--surface); }
        .nav-tabs { display: flex; gap: 8px; }
        .tab-btn { padding: 8px 16px; border-radius: 6px; font-weight: 500; font-size: 0.9rem; cursor: pointer; background: transparent; border: none; color: var(--text-muted); }
        .tab-btn.active { background: var(--surface-accent); color: var(--primary); border: 1px solid var(--border); }
        
        .chat-container { flex: 1; display: flex; flex-direction: column; overflow: hidden; padding: 24px 32px; }
        .messages-list { flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 16px; padding-right: 12px; }
        
        .msg-bubble { max-width: 75%; padding: 14px 18px; border-radius: 16px; line-height: 1.5; font-size: 0.95rem; white-space: pre-wrap; }
        .msg-user { align-self: flex-end; background: var(--primary); color: #0f172a; font-weight: 500; border-bottom-right-radius: 4px; }
        .msg-agent { align-self: flex-start; background: var(--surface); border: 1px solid var(--border); border-bottom-left-radius: 4px; }
        .agent-tag { font-size: 0.75rem; font-weight: 600; color: var(--accent); margin-bottom: 4px; display: block; }
        
        .chat-input-row { display: flex; gap: 12px; margin-top: 20px; }
        .chat-input { flex: 1; background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 14px 18px; color: var(--text); font-size: 0.95rem; outline: none; }
        .chat-input:focus { border-color: var(--primary); box-shadow: 0 0 10px var(--primary-glow); }
        
        .tab-content { display: none; flex: 1; padding: 32px; overflow-y: auto; }
        .tab-content.active { display: block; }
        
        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
        .workflow-box { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 20px; margin-bottom: 20px; }
        pre { background: #090d16; padding: 14px; border-radius: 8px; color: var(--success); font-size: 0.85rem; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="logo-title">
            <span>🏥</span> Smart Hospital AI
        </div>
        <div class="badge">Google ADK Enabled</div>
        
        <div class="card">
            <div class="card-title">Patient Profile</div>
            <div style="font-weight: 600;">Alex Taylor (PAT-1001)</div>
            <div style="font-size: 0.85rem; color: var(--text-muted);">Age 34 • Non-binary</div>
            <div style="font-size: 0.8rem; color: var(--warning); margin-top: 4px;">⚠️ Allergies: Dust mites, Penicillin</div>
        </div>

        <div class="card">
            <div class="card-title">Quick Operational Queries</div>
            <button class="btn btn-outline" onclick="sendQuick('I need to book an appointment with a dermatologist.')">📅 Book Dermatologist</button>
            <button class="btn btn-outline" onclick="sendQuick('Book my usual appointment.')">🧠 Book Usual Appt (Memory)</button>
            <button class="btn btn-outline" onclick="sendQuick('I uploaded my prescription. Explain what medicines are listed.')">📄 Read Prescription</button>
            <button class="btn btn-outline" onclick="sendQuick('What does cardiology handle and what is an ECG?')">🔎 General Info / ECG</button>
            <button class="btn btn-outline" onclick="sendQuick('Prepare a summary of my uploaded medical documents for my doctor.')">📊 Doctor Visit Summary</button>
        </div>

        <div class="card">
            <div class="card-title">ADK Callbacks & Safety</div>
            <div style="font-size: 0.8rem; color: var(--text-muted);">
                ✓ PII Auto-Redaction Active<br>
                ✓ Record Auth Verification<br>
                ✓ Medical Non-Diagnosis Guardrail
            </div>
        </div>
    </div>

    <div class="main-content">
        <div class="top-nav">
            <div class="nav-tabs">
                <button class="tab-btn active" onclick="switchTab('chat')">💬 Live Agent Chat</button>
                <button class="tab-btn" onclick="switchTab('workflows')">⚡ ADK Workflows Visualizer</button>
                <button class="tab-btn" onclick="switchTab('doctors')">👨‍⚕️ Doctors & Slots</button>
            </div>
        </div>

        <!-- Chat Tab -->
        <div id="tab-chat" class="tab-content active" style="display: flex; flex-direction: column; height: calc(100vh - 64px);">
            <div class="chat-container">
                <div class="messages-list" id="chat-messages">
                    <div class="msg-bubble msg-agent">
                        <span class="agent-tag">🤖 hospital_root_manager (Google ADK)</span>
                        Hello Alex! I am your AI Hospital Operations Assistant. How can I help you navigate appointments, prescriptions, or hospital information today?
                    </div>
                </div>
                <div class="chat-input-row">
                    <input type="text" id="user-input" class="chat-input" placeholder="Ask about doctors, slots, prescriptions, or visit summaries..." onkeydown="if(event.key==='Enter') sendMessage()">
                    <button class="btn" onclick="sendMessage()">Send Request</button>
                </div>
            </div>
        </div>

        <!-- Workflows Tab -->
        <div id="tab-workflows" class="tab-content">
            <h2 style="margin-bottom: 20px; color: var(--primary);">⚡ Google ADK Multi-Agent Workflow Visualizer</h2>
            
            <div class="workflow-box">
                <h3>1. Sequential Workflow (SequentialAgent)</h3>
                <p style="color: var(--text-muted); font-size: 0.9rem; margin: 8px 0 16px 0;">Pipeline: Patient Records (History Agent) ➔ Prescription Reader (Document Agent) ➔ Doctor Visit Summary (Report Agent)</p>
                <button class="btn" onclick="runWorkflow('sequential')">Execute Sequential Workflow</button>
                <div id="seq-output" style="margin-top: 12px;"></div>
            </div>

            <div class="workflow-box">
                <h3>2. Parallel Workflow (ParallelAgent)</h3>
                <p style="color: var(--text-muted); font-size: 0.9rem; margin: 8px 0 16px 0;">Simultaneous gathering from History Agent, Document Agent, and Appointment Agent concurrently.</p>
                <button class="btn" onclick="runWorkflow('parallel')">Execute Parallel Workflow</button>
                <div id="par-output" style="margin-top: 12px;"></div>
            </div>

            <div class="workflow-box">
                <h3>3. Quality Assurance Loop (LoopAgent)</h3>
                <p style="color: var(--text-muted); font-size: 0.9rem; margin: 8px 0 16px 0;">Evaluates document image quality score and loops up to 3 times to request re-upload if unreadable.</p>
                <button class="btn" onclick="runWorkflow('loop')">Execute Quality Check Loop</button>
                <div id="loop-output" style="margin-top: 12px;"></div>
            </div>
        </div>

        <!-- Doctors Tab -->
        <div id="tab-doctors" class="tab-content">
            <h2 style="margin-bottom: 20px; color: var(--primary);">👨‍⚕️ Hospital Doctors & Available Slots</h2>
            <div id="doctors-list" class="grid-2"></div>
        </div>
    </div>

    <script>
        function switchTab(tabName) {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            event.target.classList.add('active');
            document.getElementById('tab-' + tabName).classList.add('active');
            
            if(tabName === 'doctors') loadDoctors();
        }

        async function sendMessage() {
            const input = document.getElementById('user-input');
            const text = input.value.trim();
            if(!text) return;
            
            appendMsg(text, 'user');
            input.value = '';

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ message: text, patient_id: 'PAT-1001' })
                });
                const data = await res.json();
                appendMsg(data.reply, 'agent', data.active_agent);
            } catch(e) {
                appendMsg('Error connecting to server.', 'agent', 'System Error');
            }
        }

        function sendQuick(text) {
            document.getElementById('user-input').value = text;
            sendMessage();
        }

        function appendMsg(text, sender, agentTag = '') {
            const container = document.getElementById('chat-messages');
            const div = document.createElement('div');
            div.className = `msg-bubble msg-${sender}`;
            if(agentTag) {
                div.innerHTML = `<span class="agent-tag">🤖 ${agentTag}</span>${text}`;
            } else {
                div.textContent = text;
            }
            container.appendChild(div);
            container.scrollTop = container.scrollHeight;
        }

        async function loadDoctors() {
            const container = document.getElementById('doctors-list');
            container.innerHTML = 'Loading doctors...';
            const res = await fetch('/api/doctors');
            const docs = await res.json();
            
            const slotsRes = await fetch('/api/slots');
            const slots = await slotsRes.json();

            container.innerHTML = docs.map(d => `
                <div class="card" style="background: var(--surface);">
                    <div style="font-size: 1.1rem; font-weight: 700; color: var(--primary);">${d.name}</div>
                    <div style="color: var(--accent); font-weight: 500;">${d.department} • ⭐ ${d.rating}/5.0</div>
                    <p style="font-size: 0.85rem; color: var(--text-muted); margin: 6px 0;">${d.bio}</p>
                    <div style="font-size: 0.8rem; font-weight: 600; margin-top: 8px;">Open Slots:</div>
                    ${slots.filter(s => s.doctor_id === d.id).map(s => `
                        <div style="display:flex; justify-between; align-items:center; background: var(--surface-accent); padding: 6px 10px; border-radius: 6px; margin-top: 4px; font-size: 0.8rem;">
                            <span>📅 ${s.date} at ${s.time} (${s.slot_id})</span>
                            <button class="btn" style="padding: 4px 8px; font-size: 0.75rem;" onclick="bookSlot('${d.id}', '${s.slot_id}')">Book</button>
                        </div>
                    `).join('') || '<div style="font-size: 0.8rem; color: var(--text-muted);">No open slots right now.</div>'}
                </div>
            `).join('');
        }

        async function bookSlot(docId, slotId) {
            const res = await fetch('/api/book', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ patient_id: 'PAT-1001', doctor_id: docId, slot_id: slotId, confirmed: true })
            });
            const data = await res.json();
            if(data.success) {
                alert('✅ Appointment successfully booked! ID: ' + data.appointment.appointment_id);
                loadDoctors();
            } else {
                alert('❌ Booking failed: ' + (data.error || 'Unknown error'));
            }
        }

        async function runWorkflow(type) {
            const outDiv = document.getElementById(type + '-output');
            outDiv.innerHTML = 'Running ADK ' + type + ' workflow...';
            const res = await fetch('/api/workflows/' + type, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ patient_id: 'PAT-1001', doc_id: 'DOC-FILE-1' })
            });
            const data = await res.json();
            outDiv.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
        }
    </script>
</body>
</html>
    """)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
