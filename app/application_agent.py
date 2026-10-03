from __future__ import annotations

import json
from pathlib import Path


def load_resume_text(path: str | Path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def build_application_plan(job: dict, resume_text: str) -> dict:
    return {
        "job_title": job["title"],
        "company": job["company"],
        "location": job["location"],
        "job_url": job["url"],
        "summary": f"This role is a strong fit for a candidate with relevant experience in {job['title']} and related skills.",
        "resume_focus": [
            "Highlight measurable outcomes",
            "Align experience with role requirements",
            "Emphasize relevant tools and responsibilities",
        ],
        "next_steps": [
            "Customize the resume summary to match the job description.",
            "Draft a tailored cover letter focusing on the top three requirements.",
            "Prepare answers to likely behavioral and technical questions.",
            "Submit application and track follow-up actions.",
        ],
        "resume_preview": resume_text[:500],
    }
