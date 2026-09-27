from typing import TypedDict, List, Optional

class CoverLetterState(TypedDict):
    resume_text: str
    job_description: str
    extracted_keywords: List[str]
    draft_letter: str
    keyword_score: float
    critique: str
    iteration_count: int
    
    min_words: int
    max_words: int
    
    final_cover_letter: Optional[str]