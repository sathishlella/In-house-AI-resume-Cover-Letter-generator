from typing import List, Dict, Optional
from jinja2 import Template

BASE_SYSTEM_PROMPT = """You are a seasoned resume & cover-letter writing assistant.
Follow best practices, quantify impact, and ensure ATS-friendly formatting.
Prioritize clarity, brevity, and relevance to the target role and industry.
"""

RESUME_INSTRUCTIONS = """
Write in concise bullet points starting with strong action verbs.
Use present tense for current role and past tense for previous roles.
Quantify impact with metrics where possible (%, $, time).
Ensure keyword alignment with the given job description.
Use inclusive, professional tone. Avoid fluff and claims without evidence.
"""

COVER_LETTER_INSTRUCTIONS = """
One page max. Professional tone with warmth.
Hook in first paragraph (relevance to role & company).
Middle: 2–3 achievement paragraphs tailored to JD.
Close: enthusiasm + next-step call-to-action + availability.
"""

def build_resume_prompt(cand: Dict, job: Dict, style: Dict, existing_resume: Optional[str] = None) -> str:
    checklist = [
        "Match the target job title and domain terminology",
        "Prioritize most relevant experiences first",
        "Include top skills from the JD (without keyword stuffing)",
        "Quantify with metrics where plausible",
        "Ensure consistent tense and formatting",
        "Be ATS-friendly (plain characters, simple symbols)",
    ]
    template = Template(
        """{{ system_prompt }}
---
You will generate **a role-targeted resume** using the following inputs.

[Candidate]
Name: {{ cand.name }}
Title: {{ cand.title }}
Location: {{ cand.location }}
Email: {{ cand.email }}
Phone: {{ cand.phone }}
LinkedIn: {{ cand.linkedin }}
Portfolio: {{ cand.portfolio }}

[Core Skills]
{{ cand.skills }}

[Experience (freeform summary provided by user)]
{{ cand.experience }}

[Education & Certifications]
{{ cand.education }}

[Job Description]
Role: {{ job.title }}
Company: {{ job.company }}
Summary: {{ job.summary }}
Requirements: {{ job.requirements }}

[Style]
Tone: {{ style.tone }} | Seniority: {{ style.seniority }} | Layout: {{ style.layout }}
Constraints:
{{ resume_instructions }}

{% if existing_resume %}[Existing Resume (for context)]{{ existing_resume }}{% endif %}

Check these before finalizing:
{% for item in checklist %}- {{ item }}
{% endfor %}

Return JSON with keys:
- "summary"
- "skills"
- "experience_sections" (list of sections, each with company, role, dates, bullets)
- "projects" (optional)
- "education"
- "extras" (certs/awards/tools, etc.)
"""
    )
    return template.render(
        system_prompt=BASE_SYSTEM_PROMPT,
        cand=cand,
        job=job,
        style=style,
        resume_instructions=RESUME_INSTRUCTIONS,
        checklist=checklist,
        existing_resume=existing_resume,
    )

def build_cover_letter_prompt(cand: Dict, job: Dict, style: Dict, resume_highlights: Optional[str] = None) -> str:
    template = Template(
        """{{ system_prompt }}
---
Create a concise, tailored cover letter using the inputs below.

[Candidate]
Name: {{ cand.name }} | Title: {{ cand.title }} | Location: {{ cand.location }}
Email: {{ cand.email }} | Phone: {{ cand.phone }} | LinkedIn: {{ cand.linkedin }}

[Job]
Role: {{ job.title }}
Company: {{ job.company }}
JD Summary: {{ job.summary }}
Top Requirements: {{ job.requirements }}

[Style]
Tone: {{ style.tone }} | Seniority: {{ style.seniority }}

Constraints:
{{ cover_letter_instructions }}

Focus on alignment to the JD. If company mission is known, weave in a sentence.

Return plain Markdown (no JSON). Keep it to ~250–350 words.
{% if resume_highlights %}
Incorporate these highlights where fitting:
{{ resume_highlights }}
{% endif %}
"""
    )
    return template.render(
        system_prompt=BASE_SYSTEM_PROMPT,
        cand=cand,
        job=job,
        style=style,
        cover_letter_instructions=COVER_LETTER_INSTRUCTIONS,
        resume_highlights=resume_highlights,
    )
