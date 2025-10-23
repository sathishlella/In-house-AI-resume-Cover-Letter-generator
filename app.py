# app.py
import os
import json
import streamlit as st
from datetime import date
from jinja2 import Template

from prompts import build_resume_prompt, build_cover_letter_prompt
from utils import LLMClient, StyleConfig, safe_filename
from export import render_resume_md, render_cover_md, md_to_docx, save_docx

# ─────────────────────────────────────────────────────────────────────────────
# Read keys from Streamlit **Secrets** (Cloud) and expose them as env vars.
# In your app dashboard (Manage app → Settings → Secrets), set:
#   OPENAI_API_KEY = "sk-..."            (if using OpenAI)
#   OPENAI_MODEL   = "gpt-4o-mini"       (optional)
# OR (free tier) for Groq if you've added Groq support in utils.py:
#   GROQ_API_KEY = "gsk_..."             (if using Groq)
#   GROQ_MODEL   = "llama-3.1-8b-instant"
# ─────────────────────────────────────────────────────────────────────────────
try:
    if "OPENAI_API_KEY" in st.secrets and not os.getenv("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
    if "OPENAI_MODEL" in st.secrets and not os.getenv("OPENAI_MODEL"):
        os.environ["OPENAI_MODEL"] = st.secrets["OPENAI_MODEL"]
    if "GROQ_API_KEY" in st.secrets and not os.getenv("GROQ_API_KEY"):
        os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
    if "GROQ_MODEL" in st.secrets and not os.getenv("GROQ_MODEL"):
        os.environ["GROQ_MODEL"] = st.secrets["GROQ_MODEL"]
except Exception:
    # st.secrets may not exist locally; rely on .env for local dev
    pass

st.set_page_config(page_title="AI Resume & Cover Letter Generator", page_icon="📝", layout="wide")

# Light styling
st.markdown(
    """
<style>
.block-container { padding-top: 2rem; }
.stButton>button { border-radius: 12px; padding: 0.5rem 1rem; font-weight: 600; }
</style>
""",
    unsafe_allow_html=True,
)

st.title("📝 AI Resume & Cover Letter Generator")
st.caption("Prompt-engineered LLM app to tailor resumes and cover letters to a target job.")

# ─────────────────────────────────────────────────────────────────────────────
# Sidebar: settings
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")

    st.session_state.setdefault("style_tone", "professional, confident")
    tone = st.text_input("Tone", value=st.session_state["style_tone"], placeholder="e.g., professional, confident")
    seniority = st.selectbox("Seniority", ["entry", "junior", "mid", "mid-senior", "senior", "lead"], index=3)
    layout = st.selectbox("Layout", ["modern ATS-friendly", "classic", "two-column (ATS-safe)"], index=0)
    style = StyleConfig(tone=tone, seniority=seniority, layout=layout)

    st.divider()
    st.link_button("Advanced Settings", "pages/1_Advanced_Settings.py")

# ─────────────────────────────────────────────────────────────────────────────
# Inputs (blank by default; placeholders only)
# ─────────────────────────────────────────────────────────────────────────────
st.subheader("Candidate Profile")
col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Full Name", value=st.session_state.get("name", ""), placeholder="e.g., your name")
    title = st.text_input("Target Title", value=st.session_state.get("title", ""), placeholder="e.g., Data Analyst | GEN AI Specialist")
    location = st.text_input("Location", value=st.session_state.get("location", ""), placeholder="City, State")
    email = st.text_input("Email", value=st.session_state.get("email", ""), placeholder="you@example.com")
with col2:
    phone = st.text_input("Phone", value=st.session_state.get("phone", ""), placeholder="+1 555 123 4567")
    linkedin = st.text_input("LinkedIn URL", value=st.session_state.get("linkedin", ""), placeholder="https://linkedin.com/in/...")
    portfolio = st.text_input("Portfolio URL", value=st.session_state.get("portfolio", ""), placeholder="https://your-portfolio.com")

skills = st.text_area(
    "Core Skills (comma-separated)",
    value=st.session_state.get("skills", ""),
    placeholder="e.g., SQL, Python, Tableau, Epic, CPT/HCPCS",
)
experience = st.text_area(
    "Experience Summary (paste bullets or paragraphs)",
    height=160,
    value=st.session_state.get("experience", ""),
    placeholder="- Led ...\n- Built ...\n- Improved ...",
)
education = st.text_area(
    "Education & Certifications",
    value=st.session_state.get("education", ""),
    placeholder="e.g., MBA in Healthcare Informatics; CPC",
)

existing_resume = st.text_area(
    "Existing Resume Text (optional)",
    value=st.session_state.get("existing_resume", ""),
    help="Paste your current resume to enrich the output",
    height=120,
)

st.subheader("Target Job")
job_title = st.text_input("Job Title", value=st.session_state.get("job_title", ""), placeholder="e.g., Claims Coding Specialist")
job_company = st.text_input("Company", value=st.session_state.get("job_company", ""), placeholder="e.g., UChicago Medicine")
job_summary = st.text_area("JD Summary", value=st.session_state.get("job_summary", ""), placeholder="Paste the role summary from the job description")
job_requirements = st.text_area(
    "Top Requirements", value=st.session_state.get("job_requirements", ""), placeholder="Comma-separated top requirements"
)

# Optional sample loader (only fills when clicked)
with st.expander("Need an example? Click to load sample data", expanded=False):
    if st.button("Load sample data"):
        st.session_state.update(
            {
                "name": "your name",
                "title": "GEN AI Specialist",
                "location": "Aurora, IL",
                "email": "you@example.com",
                "phone": "+1 (555) 123-4567",
                "linkedin": "https://linkedin.com/in/yourprofile",
                "portfolio": "https://your-portfolio.com",
                "skills": "KPI Reporting, Epic, SQL, Python, Streamlit",
                "experience": "your experience",
                "education": "MBA in Healthcare Informatics; CPC (A)",
                "job_title": "Gen AI Specialist",
                "job_company": "Google",
                "job_summary": "Correct coding edits.",
                "job_requirements": "ML, AI, KPI reporting",
            }
        )
        st.rerun()

def _clear_fields():
    keys = [
        "name","title","location","email","phone","linkedin","portfolio",
        "skills","experience","education","existing_resume",
        "job_title","job_company","job_summary","job_requirements",
    ]
    for k in keys:
        st.session_state.pop(k, None)

st.button("Clear all fields", on_click=_clear_fields)

cand = {
    "name": name,
    "title": title,
    "location": location,
    "email": email,
    "phone": phone,
    "linkedin": linkedin,
    "portfolio": portfolio,
    "skills": skills,
    "experience": experience,
    "education": education,
}
job = {
    "title": job_title,
    "company": job_company,
    "summary": job_summary,
    "requirements": job_requirements,
}

# ─────────────────────────────────────────────────────────────────────────────
# Tabs: Resume / Cover Letter
# ─────────────────────────────────────────────────────────────────────────────
tab_resume, tab_cover = st.tabs(["📄 Resume", "✉️ Cover Letter"])

if "gen_resume" not in st.session_state:
    st.session_state["gen_resume"] = None
if "gen_cover" not in st.session_state:
    st.session_state["gen_cover"] = None

with tab_resume:
    st.markdown("### Generate Tailored Resume")
    if st.button("🚀 Generate Resume"):
        try:
            client = LLMClient()  # chooses OpenAI or Groq based on env/secrets (see utils.py)
            prompt = build_resume_prompt(cand, job, StyleConfig(tone=tone, seniority=seniority, layout=layout).model_dump(), existing_resume or None)
            data = client.complete_json(prompt)

            # Render Markdown using the Jinja template
            with open("templates/resume_template.md.j2", "r", encoding="utf-8") as f:
                tmpl = f.read()
            md = render_resume_md(data | {"cand": cand}, tmpl)
            st.session_state["gen_resume"] = md
            st.success("Resume generated!")
        except Exception as e:
            st.error(f"Generation error: {e}")

    if st.session_state["gen_resume"]:
        st.markdown("#### Preview (Markdown)")
        st.markdown(st.session_state["gen_resume"])
        st.download_button(
            "⬇️ Download as .md",
            data=st.session_state["gen_resume"],
            file_name=f"{safe_filename(name or 'resume')}_resume.md",
            mime="text/markdown",
        )
        # DOCX export
        doc = md_to_docx(st.session_state["gen_resume"], title=f"{name or 'Candidate'} – Resume")
        docx_path = f"{safe_filename(name or 'resume')}_resume.docx"
        save_docx(doc, docx_path)
        with open(docx_path, "rb") as fh:
            st.download_button(
                "⬇️ Download as .docx",
                data=fh,
                file_name=docx_path,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )

with tab_cover:
    st.markdown("### Generate Tailored Cover Letter")
    if st.button("✍️ Generate Cover Letter"):
        try:
            client = LLMClient()
            resume_highlights = st.session_state["gen_resume"][:2000] if st.session_state.get("gen_resume") else None
            prompt = build_cover_letter_prompt(cand, job, StyleConfig(tone=tone, seniority=seniority, layout=layout).model_dump(), resume_highlights=resume_highlights)
            md = client.complete_markdown(prompt, temperature=float(st.session_state.get("temperature", 0.6)))
            st.session_state["gen_cover"] = md
            st.success("Cover letter generated!")
        except Exception as e:
            st.error(f"Generation error: {e}")

    if st.session_state["gen_cover"]:
        st.markdown("#### Preview (Markdown)")
        st.markdown(st.session_state["gen_cover"])
        st.download_button(
            "⬇️ Download as .md",
            data=st.session_state["gen_cover"],
            file_name=f"{safe_filename(name or 'candidate')}_cover_letter.md",
            mime="text/markdown",
        )
        doc = md_to_docx(st.session_state["gen_cover"], title=f"{name or 'Candidate'} – Cover Letter")
        docx_path = f"{safe_filename(name or 'candidate')}_cover_letter.docx"
        save_docx(doc, docx_path)
        with open(docx_path, "rb") as fh:
            st.download_button(
                "⬇️ Download as .docx",
                data=fh,
                file_name=docx_path,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )

st.markdown("---")
st.caption("Built with Streamlit • Prompt engineering patterns • OpenAI/Groq API")
