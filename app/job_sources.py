from __future__ import annotations

import json
from pathlib import Path

from app.models import JobPosting


def load_jobs_from_json(path: str | Path) -> list[JobPosting]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    jobs: list[JobPosting] = []
    for job in data.get("jobs", []):
        jobs.append(
            JobPosting(
                title=job.get("title", "Unknown role"),
                company=job.get("company", "Unknown company"),
                location=job.get("location", "Remote"),
                url=job.get("url", ""),
                description=job.get("description", ""),
                source=job.get("source", "manual"),
                salary=job.get("salary"),
                employment_type=job.get("employment_type"),
                tags=job.get("tags", []),
            )
        )

    return jobs
