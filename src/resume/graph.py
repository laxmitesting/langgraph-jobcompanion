from langgraph.graph import StateGraph, START, END
from src.resume.state import ResumeState
from src.resume.nodes import (
    extract_keywords_node,
    tailor_resume_node,
    evaluate_ats_node,
    format_ats_node
)
from src.resume.edges import route_resume_draft

def build_resume_graph():
    builder = StateGraph(ResumeState)

    # Nodes
    builder.add_node("extract_keywords", extract_keywords_node)
    builder.add_node("tailor_resume", tailor_resume_node)
    builder.add_node("evaluate_ats", evaluate_ats_node)
    builder.add_node("format_ats", format_ats_node)

    # Base flow
    builder.add_edge(START, "extract_keywords")
    builder.add_edge("extract_keywords", "tailor_resume")
    builder.add_edge("tailor_resume", "evaluate_ats")

    # Conditional feedback loop
    builder.add_conditional_edges(
        "evaluate_ats",
        route_resume_draft,
        {
            "format_ats": "format_ats",
            "tailor_resume": "tailor_resume"
        }
    )

    builder.add_edge("format_ats", END)

    return builder.compile()

resume_app = build_resume_graph()