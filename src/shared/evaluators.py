import re
from typing import List, Tuple

def calculate_keyword_coverage(text: str, target_keywords: List[str]) -> Tuple[float, List[str], List[str]]:
    """Calculates keyword match ratio using regex word boundaries."""
    if not text or not target_keywords:
        return 0.0, [], target_keywords

    text_lower = text.lower()
    found = []
    missing = []

    for keyword in target_keywords:
        pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
        if re.search(pattern, text_lower):
            found.append(keyword)
        else:
            missing.append(keyword)

    score = len(found) / len(target_keywords)
    return score, found, missing