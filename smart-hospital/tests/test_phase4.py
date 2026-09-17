"""
Phase 4 Verification Tests.
Tests SequentialAgent, ParallelAgent, and LoopAgent workflow execution engines.
"""
import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from workflows.sequential_workflow import sequential_visit_summary_agent, run_sequential_workflow
from workflows.parallel_workflow import parallel_visit_prep_agent, run_parallel_workflow
from workflows.loop_workflow import document_quality_loop_agent, run_document_quality_loop

class TestPhase4(unittest.TestCase):

    def test_sequential_workflow_instantiation_and_execution(self):
        """Verify SequentialAgent workflow executes step-by-step pipeline."""
        self.assertEqual(sequential_visit_summary_agent.name, "doctor_summary_sequential_pipeline")
        
        res = run_sequential_workflow(patient_id="PAT-1001", doc_id="DOC-FILE-1")
        self.assertEqual(res["status"], "completed")
        self.assertEqual(res["workflow"], "sequential")
        self.assertEqual(len(res["steps"]), 3)
        self.assertIn("PATIENT VISIT SUMMARY", res["steps"][2]["output"])

    def test_parallel_workflow_instantiation_and_execution(self):
        """Verify ParallelAgent workflow executes concurrent information gathering."""
        self.assertEqual(parallel_visit_prep_agent.name, "visit_preparation_parallel_gatherer")
        
        res = run_parallel_workflow(patient_id="PAT-1001", doc_id="DOC-FILE-1")
        self.assertEqual(res["status"], "completed")
        self.assertEqual(res["workflow"], "parallel")
        results = res["parallel_execution_results"]
        self.assertEqual(results["patient_id"], "PAT-1001")
        self.assertIn("patient_profile", results)
        self.assertIn("document_facts", results)
        self.assertIn("appointments", results)

    def test_loop_workflow_instantiation_and_execution(self):
        """Verify LoopAgent quality check loop executes and approves high-quality documents."""
        self.assertEqual(document_quality_loop_agent.name, "document_readability_quality_loop")
        
        res = run_document_quality_loop(doc_id="DOC-FILE-1", patient_id="PAT-1001", min_quality_threshold=0.85)
        self.assertEqual(res["status"], "APPROVED")
        self.assertGreaterEqual(res["quality_score"], 0.85)

if __name__ == "__main__":
    unittest.main()
