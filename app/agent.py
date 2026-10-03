from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import APIError, OpenAI

# Load environment variables before anything else
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


def run_agent(resume_path: str | Path, jobs_path: str | Path, top_n: int = 5) -> list[dict]:
    """Run the job matching agent."""
    from app.application_agent import build_application_plan, load_resume_text
    from app.job_sources import load_jobs_from_json
    from app.resume_matcher import rank_jobs

    resume_text = load_resume_text(resume_path)
    jobs = load_jobs_from_json(jobs_path)
    ranked_jobs = rank_jobs(resume_text, jobs)

    client = OpenAIClient()
    results = []

    for item in ranked_jobs[:top_n]:
        job = {
            "title": item["title"],
            "company": item["company"],
            "location": item["location"],
            "url": item["url"],
            "description": next(
                (job.description for job in jobs if job.title == item["title"] and job.company == item["company"]), ""
            ),
            "tags": next((job.tags for job in jobs if job.title == item["title"] and job.company == item["company"]), []),
        }

        cover_letter = client.generate_cover_letter(job, resume_text)
        tailored_bullets = client.customize_resume_bullets(job, resume_text)
        interview_questions = client.generate_interview_questions(job)

        plan = build_application_plan(item, resume_text)
        results.append(
            {
                "title": item["title"],
                "company": item["company"],
                "location": item["location"],
                "score": item["score"],
                "matched_skills": item["matched_skills"],
                "missing_skills": item["missing_skills"],
                "cover_letter": cover_letter,
                "resume_bullets": tailored_bullets,
                "interview_questions": interview_questions,
                "next_step": plan["next_steps"][0],
            }
        )

    return results


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="AI job matcher with LLM-generated application materials")
    parser.add_argument("--resume", required=True, help="Path to resume text file")
    parser.add_argument("--jobs", required=True, help="Path to jobs JSON file")
    parser.add_argument("--top", type=int, default=5, help="Number of top matches to process")
    args = parser.parse_args()

    results = run_agent(args.resume, args.jobs, top_n=args.top)

    for idx, item in enumerate(results, 1):
        print(f"{idx}. {item['title']} @ {item['company']} - Score: {item['score']}/100")
        print(f"   Match: {', '.join(item['matched_skills'][:8]) or 'none'}")
        print(f"   Missing: {', '.join(item['missing_skills'][:5]) or 'none'}")
        print(f"   Next Step: {item['next_step']}")
        print(f"   Cover Letter Preview: {item['cover_letter'][:150]}...")
        print()


if __name__ == "__main__":
    main()
