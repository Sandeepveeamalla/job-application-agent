from __future__ import annotations

import argparse
from dataclasses import asdict
from pathlib import Path

from app.application_agent import build_application_plan, load_resume_text
from app.config import load_config
from app.job_sources import load_jobs_from_json
from app.llm.openai_client import OpenAIClient
from app.resume_matcher import rank_jobs


def run_agent(resume_path: str | Path, jobs_path: str | Path, top_n: int = 5) -> list[dict]:
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
            "description": next((job.description for job in jobs if job.title == item["title"] and job.company == item["company"]), ""),
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
    parser = argparse.ArgumentParser(description="AI job matcher with LLM-generated application materials")
    parser.add_argument("--resume", required=True, help="Path to resume text file")
    parser.add_argument("--jobs", required=True, help="Path to jobs JSON file")
    parser.add_argument("--top", type=int, default=5, help="Number of top matches to process")
    args = parser.parse_args()

    config = load_config()
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
