from typing import List, Tuple
from src.shared.evaluators import calculate_keyword_coverage

def evaluate_draft(
    draft: str, 
    target_keywords: List[str],
    min_words: int = 250,
    max_words: int = 450
) -> Tuple[float, str]:
    if not draft:
        return 0.0, "Draft is empty. Please generate a cover letter."

    # 1. Word Count Check
    words = draft.split()
    word_count = len(words)
    if word_count < min_words:
        length_critique = (
            f"The letter is too short ({word_count} words). "
            f"The minimum target is {min_words} words. Expand on specific achievements."
        )
    elif word_count > max_words:
        length_critique = (
            f"The letter exceeds the limit ({word_count} words). "
            f"The maximum allowed is {max_words} words. Condense and trim fluff."
        )
    else:
        length_critique = f"Word count is within the target range ({word_count} words; target: {min_words}-{max_words})."

    # 2. Shared Keyword Coverage Check
    score, found_keywords, missing_keywords = calculate_keyword_coverage(draft, target_keywords)

    # 3. Construct Critique
    critique = f"{length_critique}\nKeyword Coverage: {int(score * 100)}%.\n"
    if missing_keywords:
        critique += (
            f"Missing required keywords: {', '.join(missing_keywords)}. "
            "Integrate these naturally based on the resume."
        )

    return score, critique