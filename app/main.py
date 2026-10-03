from __future__ import annotations

import argparse
from pathlib import Path

from app.job_sources import rank_jobs
from app.job_sources import load_jobs_from_json  # noqa: F401
from app.application_agent import build_application_plan
from app.config import load_config
from app.resume_matcher import load_resume_text


def main() -> None:
    parser = argparse.ArgumentParser(description="AI job matching agent prototype")
    parser.add_argument("--resume", required=True, help="Path to resume text file")
    parser.add_argument("--jobs", required=True, help="Path to JSON file with job postings")
    parser.add_argument("--top", type=int, default=None, help="Number of top matches to display")
    args = parser.parse_args()

    config = load_config()
    resume_text = load_resume_text(args.resume)
    jobs = load_jobs_from_json(args.jobs)
    ranked_jobs = rank_jobs(resume_text, jobs)

    top_n = args.top or config.default_top_results
    for idx, job in enumerate(ranked_jobs[:top_n], 1):
        print(f"{idx}. {job['title']} @ {job['company']} - Score: {job['score']}/100")
        print(f"   Location: {job['location']}")
        print(f"   URL: {job['url']}")
        print(f"   Matched: {', '.join(job['matched_skills'][:10]) or 'none'}")
        print(f"   Missing: {', '.join(job['missing_skills'][:5]) or 'none'}")

        plan = build_application_plan(job, resume_text)
        print(f"   Suggested next step: {plan['next_steps'][0]}")
        print()


if __name__ == "__main__":
    main()
