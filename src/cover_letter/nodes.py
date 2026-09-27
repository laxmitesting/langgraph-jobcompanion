from typing import List
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from src.cover_letter.state import CoverLetterState
from src.cover_letter.tools import evaluate_draft
from src.shared.llm import parser_llm, writer_llm

from dotenv import load_dotenv; load_dotenv(override=True)

# Base LLM for drafting and polishing
llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0.3)

# Deterministic LLM for strict data extraction
parser_llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0.0)

class HybridATSParserSchema(BaseModel):
    """Schema to force the LLM to categorize skills accurately."""
    core_technical_skills: List[str] = Field(
        description="Foundational cloud, infrastructure, and programming technologies (e.g., AWS, Linux, Docker)."
    )
    cross_functional_competencies: List[str] = Field(
        description="High-value bridge skills: stakeholder communication, cross-team alignment, organizational empathy."
    )
    operational_methodologies: List[str] = Field(
        description="Workflows and operational practices: Agile, incident triage, continuous learning, root-cause analysis."
    )

def extract_keywords_node(state: CoverLetterState) -> dict:
    """
    Hybrid ATS extraction node: Extracts technical requirements AND 
    high-impact behavioral/operational competencies to highlight cross-disciplinary strength.
    """
    job_desc = state["job_description"]
    structured_llm = parser_llm.with_structured_output(HybridATSParserSchema)
    
    system_prompt = """
    You are an advanced talent acquisition parser.
    Analyze the job posting to identify both core technical proficiencies AND 
    essential cross-functional, behavioral, and operational competencies.
    
    Do not capture generic buzzwords. Capture meaningful functional and psychological competencies 
    (e.g., 'stakeholder management', 'systems thinking', 'incident triage').
    """
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Job Description:\n{job_desc}")
    ]
    
    parsed = structured_llm.invoke(messages)
    
    # Curate a balanced blend: ~4 technical anchors, ~4 operational/human anchors
    tech_targets = parsed.core_technical_skills[:4]
    bridge_targets = parsed.cross_functional_competencies[:2] + parsed.operational_methodologies[:2]
    
    balanced_keywords = tech_targets + bridge_targets
    
    unique_keywords = list({k.lower(): k for k in balanced_keywords}.values())
    
    return {"extracted_keywords": unique_keywords}


def drafter_node(state: CoverLetterState) -> dict:
    """
    Drafts or iteratively revises the cover letter based on:
    - Resume and Job Description
    - Target Keywords
    - Dynamic length constraints (min_words to max_words)
    - Prior critique feedback (if in a loop)
    """
    resume = state["resume_text"]
    job_desc = state["job_description"]
    keywords = state.get("extracted_keywords", [])
    min_w = state.get("min_words", 250)
    max_w = state.get("max_words", 450)
    prior_critique = state.get("critique", "")
    current_iteration = state.get("iteration_count", 0)

    system_instruction = (
        "You are an expert executive career coach and technical copywriter. "
        "Draft a compelling, professional cover letter tailored strictly to the candidate's resume "
        "and the target job description. Never invent experiences, metrics, or technologies."
    )

    user_prompt = f"""
    TARGET CONSTRAINTS:
    - Target length: between {min_w} and {max_w} words.
    - Required focus skills/keywords: {', '.join(keywords)}

    CANDIDATE RESUME:
    {resume}

    JOB DESCRIPTION:
    {job_desc}
    """

    if prior_critique:
        user_prompt += f"""

    PREVIOUS DRAFT FEEDBACK TO RESOLVE:
    {prior_critique}
    Please revise the letter to resolve all issues flagged above while adhering strictly to the word count.
    """

    messages = [
        SystemMessage(content=system_instruction),
        HumanMessage(content=user_prompt)
    ]
    response = llm.invoke(messages)
    draft_content = response.content.strip()

    score, feedback = evaluate_draft(
        draft=draft_content,
        target_keywords=keywords,
        min_words=min_w,
        max_words=max_w
    )

    return {
        "draft_letter": draft_content,
        "keyword_score": score,
        "critique": feedback,
        "iteration_count": current_iteration + 1
    }


def polisher_node(state: CoverLetterState) -> dict:
    """
    Final polishing node: removes generic boilerplate, ensures confident tone,
    and applies clean Markdown formatting.
    """
    draft = state["draft_letter"]
    
    prompt = f"""
    Review this finalized cover letter draft. 
    Perform a clean polish:
    1. Remove clichés (e.g., 'I am thrilled to apply', 'hard-working team player').
    2. Ensure smooth paragraph transitions and active voice.
    3. Format cleanly in Markdown with appropriate spacing, date, and placeholder sign-off.
    4. Do not alter the core facts, technical mentions, or significantly change the length.

    Cover Letter Draft:
    {draft}
    """
    response = llm.invoke([HumanMessage(content=prompt)])
    
    return {"final_cover_letter": response.content.strip()}