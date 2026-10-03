from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import APIError, OpenAI

load_dotenv()


class OpenAIClient:
    """Utility wrapper for generating tailored cover letters and interview prep."""

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not set. Add it to your environment or .env file.")

        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.client = OpenAI(api_key=self.api_key)

    def generate_cover_letter(self, job: dict[str, Any], resume_text: str, company_info: str = "") -> str:
        prompt = f"""
You are a professional career coach. Write a polished cover letter tailored to the job below.

Resume:
{resume_text}

Job Title: {job.get('title', 'Position')}
Company: {job.get('company', 'Company')}
Location: {job.get('location', 'Remote')}
Job Description:
{job.get('description', 'No description provided')}

Additional company info:
{company_info or 'Not provided'}

Requirements:
- Tailor to the exact job and company
- Highlight relevant experience and impact
- Be professional and concise
- 3 paragraphs max
- End with a strong closing sentence
"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert resume writer and career coach."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=1000,
            )
            return response.choices[0].message.content.strip()
        except APIError as exc:
            print(f"OpenAI cover letter generation failed: {exc}")
            return self._fallback_cover_letter(job)

    def customize_resume_bullets(self, job: dict[str, Any], resume_text: str) -> list[str]:
        prompt = f"""
Based on the resume and this job description, generate 5 tailored resume bullets that are relevant to the role.

Resume:
{resume_text}

Job Title: {job.get('title', 'Position')}
Company: {job.get('company', 'Company')}
Job Description:
{job.get('description', 'No description provided')}
Required Skills: {', '.join(job.get('tags', []))}

Requirements:
- Keep them concise and strong
- Use measurable outcomes where possible
- Focus on relevant experience, not generic statements
- Return only bullet points, one per line
- Use a dash at the beginning of each bullet
"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert resume coach."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=600,
            )
            text = response.choices[0].message.content.strip()
            bullets = []
            for line in text.splitlines():
                cleaned = line.strip()
                if cleaned:
                    bullets.append(cleaned.lstrip("- ").strip())
            return bullets[:5]
        except APIError as exc:
            print(f"OpenAI resume bullet generation failed: {exc}")
            return [
                f"Delivered impactful work aligned with {job.get('title', 'the role')} responsibilities.",
                f"Applied core skills in {', '.join(job.get('tags', [])[:3]) or 'relevant technologies'} to solve real business problems.",
                "Improved team delivery speed through strong execution and collaboration.",
                "Worked with cross-functional stakeholders to build and deliver reliable software solutions.",
                "Focused on measurable outcomes, quality, and maintainability.",
            ]

    def generate_interview_questions(self, job: dict[str, Any]) -> list[dict[str, str]]:
        prompt = f"""
Generate 5 likely interview questions for this job role along with a brief hint and sample answer approach.

Job title: {job.get('title', 'Position')}
Company: {job.get('company', 'Company')}
Role description:
{job.get('description', 'No description provided')}

Return valid JSON in this format:
[
  {{
    "question": "...",
    "hint": "...",
    "example_answer": "..."
  }}
]
"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an interview preparation coach."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=1200,
            )
            content = response.choices[0].message.content.strip()
            start = content.find("[")
            end = content.rfind("]") + 1
            if start >= 0 and end > start:
                return json.loads(content[start:end])
            return []
        except (APIError, json.JSONDecodeError) as exc:
            print(f"OpenAI interview generation failed: {exc}")
            return []

    def _fallback_cover_letter(self, job: dict[str, Any]) -> str:
        title = job.get("title", "Role")
        company = job.get("company", "the company")
        return f"""
Dear Hiring Manager,

I am excited to apply for the {title} position at {company}. I believe my background, strong technical skills, and ability to solve real-world problems make me a strong fit for this role.

In my previous work, I have focused on building reliable systems, collaborating with teams, and delivering outcomes that improve product quality and business performance. I am particularly interested in the opportunity to contribute to {company} and work on meaningful challenges in this space.

I would welcome the opportunity to discuss how my experience and skills align with your needs. Thank you for your time and consideration.

Sincerely,
[Your Name]
"""


if __name__ == "__main__":
    client = OpenAIClient()
    sample_job = {
        "title": "Senior Python Engineer",
        "company": "Acme Labs",
        "location": "Remote",
        "description": "Build APIs and backend systems in Python. Experience with cloud systems and testing is important.",
        "tags": ["python", "api", "backend", "aws"],
    }
    sample_resume = "Experienced Python engineer with backend systems, API work, testing, and cloud deployment."
    print(client.generate_cover_letter(sample_job, sample_resume))
