import os, json
from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class StyleConfig(BaseModel):
    tone: str = Field(default="professional, confident")
    seniority: str = Field(default="mid-senior")
    layout: str = Field(default="modern ATS-friendly")

class LLMClient:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        if not self.api_key:
            raise RuntimeError("Missing OPENAI_API_KEY. Set it in .env or Streamlit Secrets.")
        self.client = OpenAI(api_key=self.api_key)

    def complete_json(self, prompt: str) -> dict:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Return strictly valid JSON unless told otherwise."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
        )
        text = resp.choices[0].message.content
        # attempt to find JSON block
        try:
            start = text.find("{")
            end = text.rfind("}")
            return json.loads(text[start:end+1])
        except Exception as e:
            raise ValueError(f"Model did not return valid JSON. Raw: {text[:500]}")

    def complete_markdown(self, prompt: str, temperature: float = 0.6) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Return clean Markdown."},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
        )
        return resp.choices[0].message.content

def safe_filename(name: str) -> str:
    return "".join(c for c in name if c.isalnum() or c in "._- ").strip().replace(" ", "_") or "output"

