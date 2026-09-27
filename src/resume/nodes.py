from langchain_core.messages import HumanMessage, SystemMessage
from src.shared.llm import parser_llm, writer_llm
from src.resume.state import ResumeState
from src.resume.schema import ResumeSchema
from src.resume.tools import evaluate_resume_draft


def extract_keywords_node(state: ResumeState) -> dict:
    """Extracts high-priority ATS keywords from the JD."""
    sys_msg = SystemMessage(
        content=(
            "You are an expert talent acquisition specialist and ATS parsing engine. "
            "Analyze the target job description to identify the 10 to 15 highest-priority requirement signals.\n\n"
            "Extraction Priorities:\n"
            "- Target the role's core functional domain: extract technical proficiencies, platforms, and methodologies for engineering roles; extract deal stages, client strategy, and commercial competencies for sales/account roles.\n"
            "- Extract domain-specific tools, platforms, execution frameworks, and core operational disciplines required by the role.\n"
            "- Avoid generic corporate fluff (e.g., do not include 'fast-paced environment', 'team player', or 'self-starter').\n"
            "- Normalize multi-word phrases so they match standard industry terms.\n\n"
            "Output Format:\n"
            "- Return strictly a flat, comma-separated list of terms (e.g., Term 1, Term 2, Term 3).\n"
            "- Do not include numbering, bullet points, introductory remarks, or markdown backticks."
        )
    )
    user_msg = HumanMessage(content=f"Job Description:\n{state['job_description']}")
    response = parser_llm.invoke([sys_msg, user_msg])
    keywords = [k.strip() for k in response.content.split(",") if k.strip()]

    return {
        "extracted_keywords": keywords,
        "iteration_count": 0,
        "ats_match_score": 0.0,
        "evaluation_feedback": "",
        "structured_resume": None,
        "final_ats_resume": ""
    }


def tailor_resume_node(state: ResumeState) -> dict:
    """Drafts a concise tailored resume emphasizing key skills without hallucinating."""
    feedback = state.get("evaluation_feedback", "")
    iteration = state.get("iteration_count", 0) + 1

    sys_msg = SystemMessage(
        content=(
            "You are an executive resume writer specializing in high-density, concise resumes.\n"
            "Rules:\n"
            "- Target length: Strict 1 to 2 pages (max 650 words).\n"
            "- Select ONLY past roles, achievements, and skills strictly relevant to the job.\n"
            "- Keep 2-3 impactful bullet points per role, using strong action verbs.\n"
            "- Do NOT fabricate metrics, titles, or experience."
        )
    )

    prompt = (
        f"Target Keywords:\n{', '.join(state['extracted_keywords'])}\n\n"
        f"Master Resume:\n{state['master_resume']}\n\n"
    )
    if feedback:
        prompt += f"Previous Iteration Feedback to address:\n{feedback}\n\n"

    prompt += "Draft the tailored resume content:"
    response = writer_llm.invoke([sys_msg, HumanMessage(content=prompt)])

    return {
        "draft_resume": response.content,
        "iteration_count": iteration
    }


def evaluate_ats_node(state: ResumeState) -> dict:
    """Zero-token programmatic ATS scoring using regex tools."""
    score, critique = evaluate_resume_draft(
        draft=state.get("draft_resume", ""),
        target_keywords=state.get("extracted_keywords", [])
    )
    return {
        "ats_match_score": score,
        "evaluation_feedback": critique
    }


def format_ats_node(state: ResumeState) -> dict:
    """Uses structured output to convert drafted resume into strict ResumeSchema."""
    structured_llm = parser_llm.with_structured_output(ResumeSchema)

    sys_msg = SystemMessage(
        content=(
            "You are an ATS compliance and structuring engine. "
            "Extract and map the drafted resume into the structured schema.\n"
            "Rules:\n"
            "- Strictly maintain 2-3 high-impact bullet points per experience item.\n"
            "- Group skills into 3 to 5 coherent categories formatted exactly as 'Category Name: Item 1, Item 2, Item 3'.\n"
            "- The skill category names must organically reflect the target role domain (e.g., align categories with Technical/Engineering, Sales/Account Strategy, or Management depending on what the drafted resume emphasizes).\n"
            "- Only include skills explicitly substantiated by the candidate's base experience; do not invent missing tools or capabilities.\n"
            "- Condense certifications into clean, standard official titles without descriptions.\n"
            "- Strip all trailing newlines, markdown fences, and redundant whitespaces within list items."
        )
    )
    user_msg = HumanMessage(
        content=(
            f"Drafted Resume:\n{state['draft_resume']}\n\n"
            f"Master Resume Reference:\n{state['master_resume']}"
        )
    )

    structured_data: ResumeSchema = structured_llm.invoke([sys_msg, user_msg])
    resume_dict = structured_data.model_dump()

    # Create a clean, fallback plain text version
    lines = []
    if resume_dict.get("full_name"):
        lines.append(resume_dict["full_name"])
    if resume_dict.get("contact_info"):
        lines.append(resume_dict["contact_info"])
    if resume_dict.get("summary"):
        lines.append(f"\nSUMMARY\n{resume_dict['summary']}")
    
    if resume_dict.get("skills"):
        lines.append("\nTECHNICAL SKILLS")
        for skill_group in resume_dict["skills"]:
            lines.append(f"• {skill_group}")

    if resume_dict.get("experience"):
        lines.append("\nPROFESSIONAL EXPERIENCE")
        for exp in resume_dict["experience"]:
            header = f"{exp['title']} | {exp['company']} | {exp['dates']}"
            if exp.get("location"):
                header += f" | {exp['location']}"
            lines.append(header)
            for bullet in exp.get("bullets", []):
                lines.append(f"  • {bullet}")

    if resume_dict.get("education"):
        lines.append("\nEDUCATION")
        for edu in resume_dict["education"]:
            lines.append(f"{edu['degree']} — {edu['institution']} ({edu.get('dates', '')})")

    if resume_dict.get("certifications"):
        lines.append(f"\nCERTIFICATIONS: {', '.join(resume_dict['certifications'])}")

    fallback_text = "\n".join(lines)

    return {
        "structured_resume": resume_dict,
        "final_ats_resume": fallback_text
    }