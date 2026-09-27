from src.resume.state import ResumeState

def route_resume_draft(state: ResumeState) -> str:
    """
    Evaluates ATS match quality to determine the next node.
    Routes to 'format_ats' if score passes threshold or iteration limit is reached.
    Otherwise, loops back to 'tailor_resume' for revision.
    """
    score = state.get("ats_match_score", 0.0)
    iterations = state.get("iteration_count", 0)

    PASSING_SCORE = 0.8  # 80% keyword alignment
    MAX_ITERATIONS = 3   # Prevent infinite loops

    if score >= PASSING_SCORE or iterations >= MAX_ITERATIONS:
        return "format_ats"
    
    return "tailor_resume"