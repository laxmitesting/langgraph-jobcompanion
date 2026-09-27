import streamlit as st
import uuid
import re
from dotenv import load_dotenv
from datetime import date

# Feature modularized graph imports
from src.cover_letter.graph import compiled_graph as cover_letter_app
from src.resume.graph import resume_app

# Shared export builders
from src.shared.export import (
    build_resume_docx,
    build_cover_letter_docx,
    html_to_pdf_bytes,
    is_pdf_available
)

load_dotenv(override=True)

st.set_page_config(
    page_title="Job Companion ✧ Studio",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Styling - Aggressive Light Theme Reset for Dark Mode
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* 1. Remove native Streamlit top header bar */
    header[data-testid="stHeader"] { display: none !important; }
    .main .block-container { padding-top: 2rem !important; padding-bottom: 2rem !important; }
    
    .stApp { font-family: 'Inter', sans-serif !important; }
    h1, h2, h3, h4 { font-family: 'Inter', sans-serif !important; letter-spacing: -0.02em; }

    /* 2. Tabs - Minimal aesthetic overrides */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; border-bottom: 1px solid #ECEAE5; margin-bottom: 18px; }
    .stTabs [data-baseweb="tab"] { height: 42px; border-radius: 8px 8px 0 0; }
    .stTabs [aria-selected="true"] { border-bottom: 2px solid #3B3273 !important; }

    /* 3. Badges & Export Buttons */
    .stButton>button, .stDownloadButton>button { border-radius: 8px !important; font-weight: 600 !important; }
    .stat-pill { display: inline-block; padding: 5px 12px; border-radius: 18px; background-color: #F4F1EA; border: 1px solid #E6E1D6; font-size: 12px; font-weight: 600; color: #433B32; margin-right: 8px; }
    .badge { display: inline-flex; padding: 2px 8px; margin: 2px 3px 2px 0; border-radius: 10px; font-size: 11px; font-weight: 600; background-color: #EAE6FF; color: #3B3273; border: 1px solid #D4CEFA; }

    /* 4. Document Sheets */
    .resume-sheet { background-color: #FFFFFF; color: #111111; padding: 34px 40px; border: 1px solid #D8D8D8; box-shadow: 0 4px 16px rgba(0,0,0,0.05); font-family: 'Times New Roman', Times, Georgia, serif; line-height: 1.4; font-size: 14px; }
    .resume-name { font-size: 22px; font-weight: bold; text-align: center; text-transform: uppercase; margin-bottom: 2px; }
    .resume-contact { font-size: 13px; text-align: center; color: #333333; margin-bottom: 16px; }
    .resume-section-title { font-size: 13.5px; font-weight: bold; text-transform: uppercase; border-bottom: 1px solid #222222; margin-top: 14px; margin-bottom: 6px; }
    .role-header { display: flex; justify-content: space-between; margin-top: 6px; }
    
    .doc-preview-letter { background-color: #FAFAFA; color: #1F2421; padding: 32px 36px; border: 1px solid #E6E8EA; box-shadow: 0 4px 20px rgba(0,0,0,0.03); font-family: 'Calibri', 'Inter', sans-serif; font-size: 15px; line-height: 1.6; white-space: pre-wrap; }
</style>
""", unsafe_allow_html=True)

def render_structured_resume_html(data: dict) -> str:
    html = ['<div class="resume-sheet">']
    if data.get("full_name"): html.append(f'<div class="resume-name">{data["full_name"]}</div>')
    if data.get("contact_info"): html.append(f'<div class="resume-contact">{data["contact_info"]}</div>')
    if data.get("summary"):
        html.append('<div class="resume-section-title">Professional Summary</div>')
        html.append(f'<div style="margin-bottom: 8px;">{data["summary"]}</div>')
    if data.get("experience"):
        html.append('<div class="resume-section-title">Professional Experience</div>')
        for exp in data["experience"]:
            title = exp.get("title", "")
            company = exp.get("company", "")
            dates = exp.get("dates", "")
            loc_str = f" | {exp.get('location', '')}" if exp.get("location") else ""
            html.append(f'<div class="role-header"><span style="font-weight:bold;">{title} — {company}</span><span style="font-style:italic;">{dates}{loc_str}</span></div>')
            bullets = exp.get("bullets", [])
            if bullets:
                html.append('<ul style="margin:2px 0 6px 0; padding-left:20px;">')
                for b in bullets: html.append(f'<li style="margin-bottom:2px;">{b}</li>')
                html.append('</ul>')
    if data.get("skills"):
        html.append('<div class="resume-section-title">Technical Skills</div>')
        for skill in data["skills"]: html.append(f'<div style="margin:3px 0;">• {skill}</div>')
    if data.get("education"):
        html.append('<div class="resume-section-title">Education</div>')
        for edu in data["education"]:
            date_str = f" ({edu.get('dates', '')})" if edu.get("dates") else ""
            html.append(f'<div style="margin:3px 0;"><b>{edu.get("degree", "")}</b> — {edu.get("institution", "")}{date_str}</div>')
    if data.get("certifications"):
        html.append('<div class="resume-section-title">Certifications</div>')
        html.append(f'<div style="margin:3px 0;">• {", ".join(data["certifications"])}</div>')
    html.append('</div>')
    return "".join(html)

st.title("💼 ✧ Job Companion Studio")
st.caption("A multi-agent intelligence workspace tailoring high-impact ATS resumes & compelling cover letters.")

if "thread_id" not in st.session_state: st.session_state.thread_id = str(uuid.uuid4())
if "resume_output" not in st.session_state: st.session_state.resume_output = None
if "letter_output" not in st.session_state: st.session_state.letter_output = None

workspace_left, workspace_right = st.columns([1, 1.25], gap="large")

with workspace_left:
    st.subheader("1. Profile & Target Context")
    master_resume_input = st.text_area("Master Base Resume", height=280, placeholder="Paste your comprehensive background, accomplishments, and skills here...")
    job_desc_input = st.text_area("Job Description (JD)", height=280, placeholder="Paste target job requirements and key responsibilities...")

with workspace_right:
    st.subheader("2. Generated Artifacts")
    tab_resume, tab_letter = st.tabs(["📄 Tailored ATS Resume", "✉️ Strategic Cover Letter"])

    with tab_resume:
        generate_resume_btn = st.button("✧ Generate ATS Resume", key="gen_resume_btn")
        if generate_resume_btn:
            if not master_resume_input or not job_desc_input: st.warning("Please provide both a Master Resume and a Job Description.")
            else:
                with st.spinner("Extracting technical requirements, structuring data, and validating ATS density..."):
                    st.session_state.resume_output = resume_app.invoke(
                        {"master_resume": master_resume_input, "job_description": job_desc_input}, 
                        config={"configurable": {"thread_id": f"{st.session_state.thread_id}-resume"}}
                    )
        
        if st.session_state.resume_output:
            res = st.session_state.resume_output
            st.markdown(f'<div style="margin: 12px 0 14px 0;"><span class="stat-pill">🎯 ATS Match: {res.get("ats_match_score", 0)*100:.0f}%</span><span class="stat-pill">🔁 Revisions: {res.get("iteration_count", 1)}</span></div>', unsafe_allow_html=True)
            
            keywords = res.get("extracted_keywords", [])
            if keywords: st.markdown(f'<div style="margin-bottom: 12px;">{"".join([f"<span class=badge>{k}</span>" for k in keywords])}</div>', unsafe_allow_html=True)

            structured_data = res.get("structured_resume")
            rendered_html = render_structured_resume_html(structured_data) if structured_data else None

            if structured_data:
                st.markdown("**Export Options:**")
                exp_c1, exp_c2 = st.columns([1, 1])
                with exp_c1: st.download_button("📥 Download Word (.docx)", data=build_resume_docx(structured_data), file_name="tailored_ats_resume.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", key="dl_res_docx")
                with exp_c2:
                    if is_pdf_available() and rendered_html: st.download_button("📄 Download PDF (.pdf)", data=html_to_pdf_bytes(rendered_html, "resume"), file_name="tailored_ats_resume.pdf", mime="application/pdf", key="dl_res_pdf")
                    else: st.caption("ℹ️ *PDF export unavailable. Use .docx*")

            if rendered_html: st.markdown(rendered_html, unsafe_allow_html=True)
            else: st.markdown(f'<div class="resume-sheet" style="white-space: pre-wrap;">{re.sub(r"\\n{3,}", "\\n\\n", res.get("final_ats_resume", ""))}</div>', unsafe_allow_html=True)

            with st.expander("View Resume Agent Feedback"): st.markdown(res.get("evaluation_feedback", "No feedback recorded."))

    with tab_letter:
        with st.expander("⚙️ Length & Word Constraints", expanded=False):
            c1, c2 = st.columns(2)
            with c1: min_words_input = st.number_input("Min Words", value=250, step=25)
            with c2: max_words_input = st.number_input("Max Words", value=450, step=25)

        generate_letter_btn = st.button("✧ Draft Cover Letter", key="gen_letter_btn")
        if generate_letter_btn:
            if not master_resume_input or not job_desc_input: st.warning("Please provide both a Master Resume and a Job Description.")
            else:
                with st.spinner("Synthesizing narrative tone and optimizing word boundaries..."):
                    st.session_state.letter_output = cover_letter_app.invoke(
                        {"resume_text": master_resume_input, "job_description": job_desc_input, "min_words": min_words_input, "max_words": max_words_input},
                        config={"configurable": {"thread_id": f"{st.session_state.thread_id}-letter"}}
                    )

        if st.session_state.letter_output:
            cl = st.session_state.letter_output
            st.markdown(f'<div style="margin: 12px 0 14px 0;"><span class="stat-pill">📊 Keyword Alignment: {cl.get("keyword_score", 0)*100:.0f}%</span><span class="stat-pill">🔁 Revisions: {cl.get("iteration_count", 0)}</span></div>', unsafe_allow_html=True)
            
            cl_keywords = cl.get("extracted_keywords", [])
            if cl_keywords: st.markdown(f'<div style="margin-bottom: 12px;">{"".join([f"<span class=badge>{k}</span>" for k in cl_keywords])}</div>', unsafe_allow_html=True)
            # 1. Base clean
            clean_letter = re.sub(r'\n{3,}', '\n\n', cl.get("final_cover_letter", "").replace("```markdown", "").replace("```", "").strip())

            # 2. Date replacement
            today_str = date.today().strftime("%B %d, %Y")
            clean_letter = re.sub(r'(\*{0,2})\[(?:Today[’\']s\s+)?Date\](\*{0,2})', today_str, clean_letter, flags=re.IGNORECASE)

            # 3. Strip bold markdown artifacts
            clean_letter = re.sub(r'\*\*(.*?)\*\*', r'\1', clean_letter)

            # 4. Drop redundant top name so letter starts cleanly at the Date
            if today_str in clean_letter and not clean_letter.startswith(today_str):
                clean_letter = re.sub(rf'^.*?(?={re.escape(today_str)})', '', clean_letter, flags=re.DOTALL).strip()

            # Dual Export Action Row
            st.markdown("**Export Options:**")
            cl_exp_c1, cl_exp_c2 = st.columns([1, 1])
            with cl_exp_c1: st.download_button("📥 Download Word (.docx)", data=build_cover_letter_docx(clean_letter), file_name="tailored_cover_letter.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", key="dl_let_docx")
            with cl_exp_c2:
                if is_pdf_available(): st.download_button("📄 Download PDF (.pdf)", data=html_to_pdf_bytes("".join([f"<p>{p.strip()}</p>" for p in clean_letter.split("\n\n") if p.strip()]), "cover_letter"), file_name="tailored_cover_letter.pdf", mime="application/pdf", key="dl_let_pdf")
                else: st.caption("ℹ️ *PDF export unavailable. Use .docx*")

            st.markdown(f'<div class="doc-preview-letter">{clean_letter}</div>', unsafe_allow_html=True)
            with st.expander("View Cover Letter Agent Diagnostics"): st.markdown(cl.get("critique", "No critique available."))