from langgraph.graph import END, StateGraph
from .nodes import extract_complaint, validate_complaint
from .state import ComplaintState


workflow = StateGraph(ComplaintState)
workflow.add_node("extract_complaint", extract_complaint)
workflow.add_node("validate_complaint", validate_complaint)
workflow.set_entry_point("extract_complaint")
workflow.add_edge("extract_complaint", "validate_complaint")
workflow.add_edge("validate_complaint", END)
complaint_graph = workflow.compile()

