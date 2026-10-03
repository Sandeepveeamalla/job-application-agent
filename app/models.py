from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class JobPosting:
    title: str
    company: str
    location: str
    url: str
    description: str
    source: str = "manual"
    salary: str | None = None
    employment_type: str | None = None
    tags: List[str] = field(default_factory=list)
