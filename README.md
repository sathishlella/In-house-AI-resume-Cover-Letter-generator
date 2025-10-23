# AI Resume & Cover Letter Generator (Streamlit)

**Category:** NLP  
**Skills:** Prompt engineering, LLM text generation  
**Deployment:** Streamlit Cloud

This app generates a tailored resume and cover letter from your inputs and a target job description.
It uses modular prompt templates and lets you export polished DOCX files.

## Features
- Guided form for candidate profile and target job description
- Optional upload of existing resume text to enrich outputs
- Template-based generation (choose tone/format)
- Live preview of resume sections and cover letter
- One-click export as DOCX (and copyable Markdown)
- Advanced settings: model, temperature, length, and style presets
- Prompt engineering patterns: role prompting, constraints, checklists

## Quickstart (Local)
1. **Python 3.10+** recommended.
2. `pip install -r requirements.txt`
3. Create a `.env` file with:
   ```env
   OPENAI_API_KEY=your_key_here
   OPENAI_MODEL=gpt-4o-mini
   ```
4. Run:
   ```bash
   streamlit run app.py
   ```

## Deploy to Streamlit Cloud
1. Push this folder to a new **public GitHub repo**.
2. On [share.streamlit.io](https://share.streamlit.io), create a new app:
   - **Repository:** your/repo
   - **Branch:** main
   - **Main file path:** `app.py`
   - Add a **SECRETS** entry with your OpenAI key:
     ```toml
     OPENAI_API_KEY="your_key_here"
     OPENAI_MODEL="gpt-4o-mini"
     ```
3. Click **Deploy**. Your app will be live in ~1–2 minutes.

## Project Structure
```
ai-resume-coverletter-generator/
├─ app.py               # Main Streamlit app
├─ prompts.py           # Prompt templates & builders
├─ utils.py             # LLM client, helpers
├─ export.py            # DOCX/Markdown exporters
├─ pages/
│  └─ 1_Advanced_Settings.py  # Advanced knobs & style presets
├─ templates/
│  ├─ resume_template.md.j2
│  └─ cover_letter_template.md.j2
├─ .streamlit/
│  └─ config.toml       # Theming
├─ requirements.txt
├─ README.md
└─ .env.example
```

## Notes
- The app defaults to `gpt-4o-mini`. You can switch models under **Advanced Settings**.
- Streamlit Cloud uses **Secrets**; local dev uses `.env`.
- If PDF is needed, export DOCX then save as PDF in Word/Google Docs (lightest dependency path).
