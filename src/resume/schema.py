from typing import List, Optional
from pydantic import BaseModel, Field


class ExperienceItem(BaseModel):
    title: str = Field(
        description="Official role or job title (e.g., 'Trainee Google Cloud Platform Engineer')."
    )
    company: str = Field(
        description="Company, institution, or organization name."
    )
    dates: str = Field(
        description="Date or duration range (e.g., 'August 2022 – November 2022' or '2024 – Present')."
    )
    location: Optional[str] = Field(
        default="",
        description="City, State/Country or 'Remote' (e.g., 'London, UK')."
    )
    bullets: List[str] = Field(
        description="2 to 3 concise, impact-oriented bullet points. No trailing newlines or blank items."
    )


class EducationItem(BaseModel):
    institution: str = Field(description="University, college, or school name.")
    degree: str = Field(description="Degree or program title (e.g., 'BSc Computer Science').")
    dates: Optional[str] = Field(default="", description="Year or date range (e.g., '2019 – 2022').")
    details: Optional[str] = Field(
        default="",
        description="Optional brief honors, GPA, or notable coursework."
    )


class ResumeSchema(BaseModel):
    full_name: Optional[str] = Field(default="", description="Candidate full name if provided in master resume.")
    contact_info: Optional[str] = Field(
        default="",
        description="Contact headline (e.g., 'London, UK | linkedin.com/in/... | email@domain.com')."
    )
    summary: Optional[str] = Field(
        default="",
        description="A concise 2-3 sentence executive summary tailored to the role."
    )
    skills: List[str] = Field(
        description=(
            "Grouped skill categories as single strings (e.g., "
            "'Cloud & DevOps: GCP, Kubernetes, Docker, CI/CD', "
            "'Programming: Python, Shell Scripting')."
        )
    )
    experience: List[ExperienceItem] = Field(
        description="Strictly prioritized relevant roles, ordered reverse-chronologically."
    )
    education: List[EducationItem] = Field(
        default_factory=list,
        description="List of education items."
    )
    certifications: List[str] = Field(
        default_factory=list,
        description="List of certification names without bullet points (e.g., 'Ethics of AI', 'Google Cloud Professional Architect')."
    )