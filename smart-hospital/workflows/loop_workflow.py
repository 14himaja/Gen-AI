"""
Loop Workflow Engine for Smart Hospital.
Demonstrates Google ADK Concept #5: Loop Workflow (LoopAgent).
Evaluates document readability and quality, looping to request re-upload if quality score < threshold.
"""
import sys
import os
from typing import Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from google.adk.agents import Agent, LoopAgent
from tools.hospital_tools import read_document

# Instantiate dedicated sub-agent instance for LoopAgent
loop_document_agent = Agent(
    model="gemini-2.0-flash",
    name="loop_document_agent",
    description="Evaluates document quality in loop.",
    instruction="Read document and evaluate quality.",
    tools=[read_document]
)

document_quality_loop_agent = LoopAgent(
    name="document_readability_quality_loop",
    sub_agents=[
        loop_document_agent
    ],
    max_iterations=3
)

def run_document_quality_loop(doc_id: str, patient_id: str = "PAT-1001", min_quality_threshold: float = 0.85) -> Dict[str, Any]:
    """
    Executes a quality check loop:
    1. Read document.
    2. Check quality score.
    3. If quality >= threshold: PASS (APPROVED).
    4. If quality < threshold: LOOP & request better document upload.
    """
    iteration = 0
    max_loops = 3
    doc_data = {}
    
    while iteration < max_loops:
        iteration += 1
        doc_data = read_document(doc_id, patient_id)
        quality = doc_data.get("quality_score", 1.0)

        if quality >= min_quality_threshold:
            return {
                "status": "APPROVED",
                "iterations_taken": iteration,
                "quality_score": quality,
                "document": doc_data,
                "message": "Document quality passed verification."
            }
        else:
            if iteration == max_loops:
                break

    return {
        "status": "RE-UPLOAD_REQUESTED",
        "iterations_taken": iteration,
        "quality_score": doc_data.get("quality_score", 0.0),
        "message": "Document image quality is too low or blurry. Please re-upload a clearer image."
    }
