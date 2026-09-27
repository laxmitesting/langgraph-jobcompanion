from typing import TypedDict, List, Optional

class ResumeState(TypedDict):
    master_resume: str
    job_description: str
    extracted_keywords: List[str]
    draft_resume: str
    structured_resume: Optional[dict]  
    final_ats_resume: str              
    ats_match_score: float             
    evaluation_feedback: str          
    iteration_count: int              