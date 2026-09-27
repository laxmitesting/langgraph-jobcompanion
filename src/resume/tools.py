from typing import List, Tuple
from src.shared.evaluators import calculate_keyword_coverage

ATS_STANDARD_SECTIONS = ["experience", "skills", "education"]

def evaluate_resume_draft(
    draft: str, 
    target_keywords: List[str],
    max_words: int = 700
) -> Tuple[float, str]:
    """
    Evaluates the drafted resume for keyword presence, ATS sections,
    and page density constraints.
    """
    if not draft:
        return 0.0, "Draft is empty."

    draft_lower = draft.lower()
    
    # 1. Standard Section Presence Check
    missing_sections = [
        sec for sec in ATS_STANDARD_SECTIONS 
        if sec not in draft_lower
    ]

    # 2. Shared Keyword Coverage via Regex
    score, _, missing_keywords = calculate_keyword_coverage(draft, target_keywords)

    # 3. Density & Word Count Check (Enforce 1-2 page budget)
    word_count = len(draft.split())
    critique_parts = [f"Keyword Match: {int(score * 100)}% ({word_count} words)."]

    if word_count > max_words:
        critique_parts.append(
            f"Draft is too long ({word_count} words, max recommended is {max_words}). "
            "Condense bullet points and remove less relevant past roles to preserve a 1-2 page profile."
        )

    if missing_keywords:
        critique_parts.append(
            f"Missing target keywords: {', '.join(missing_keywords)}. "
            "Integrate these naturally into relevant experience or skill lines."
        )

    if missing_sections:
        critique_parts.append(
            f"Missing core ATS sections: {', '.join(missing_sections).title()}."
        )

    critique = "\n".join(critique_parts)
    return score, critique