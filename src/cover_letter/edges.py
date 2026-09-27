from src.cover_letter.state import CoverLetterState

def route_draft(state: CoverLetterState) -> str:
    """
    Evaluates the current state to determine the next node.
    Routes to 'polisher' if the draft passes criteria or hits the loop limit.
    Otherwise, routes back to 'drafter' for revision.
    """
    score = state.get("keyword_score", 0.0)
    iterations = state.get("iteration_count", 0)
    
    # Define thresholds
    PASSING_SCORE = 0.8  # 80% keyword/competency coverage
    MAX_ITERATIONS = 3   # Prevent infinite API loops

    # 1. Did it pass the evaluation?
    if score >= PASSING_SCORE:
        return "polisher_node"
    
    # 2. Did it run out of retries?
    if iterations >= MAX_ITERATIONS:
        return "polisher_node"
    
    # 3. Needs revision
    return "drafter_node"