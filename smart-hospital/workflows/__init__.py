"""Google ADK Workflows Package for Smart Hospital."""
from .sequential_workflow import sequential_visit_summary_agent, run_sequential_workflow
from .parallel_workflow import parallel_visit_prep_agent, run_parallel_workflow
from .loop_workflow import document_quality_loop_agent, run_document_quality_loop

__all__ = [
    "sequential_visit_summary_agent",
    "run_sequential_workflow",
    "parallel_visit_prep_agent",
    "run_parallel_workflow",
    "document_quality_loop_agent",
    "run_document_quality_loop"
]
