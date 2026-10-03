from __future__ import annotations

import re
from typing import Iterable


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s+\-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_keywords(text: str, min_word_length: int = 3) -> set[str]:
    cleaned = normalize_text(text)
    words = cleaned.split()
    keywords = set()

    for word in words:
        if len(word) >= min_word_length and not word.isdigit():
            keywords.add(word)

    return keywords


def score_job_match(resume_text: str, job: object) -> tuple[int, list[str], list[str]]:
    resume_keywords = extract_keywords(resume_text)
    job_text = f"{job.title} {job.description} {' '.join(job.tags)}"
    job_keywords = extract_keywords(job_text)

    matched = sorted(resume_keywords & job_keywords)
    missing = sorted(job_keywords - resume_keywords)

    score = min(100, max(0, int((len(matched) / max(1, len(job_keywords))) * 100)))
    return score, matched, missing


def rank_jobs(resume_text: str, jobs: Iterable[object]) -> list[dict]:
    ranked = []
    for job in jobs:
        score, matched, missing = score_job_match(resume_text, job)
        ranked.append(
            {
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "url": job.url,
                "source": job.source,
                "score": score,
                "matched_skills": matched,
                "missing_skills": missing[:10],
            }
        )

    return sorted(ranked, key=lambda item: item["score"], reverse=True)
