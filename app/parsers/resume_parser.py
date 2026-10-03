from __future__ import annotations

import re
from pathlib import Path
from typing import Any

try:
    from docx import Document
except ImportError:
    Document = None

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None


class ResumeParser:
    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)
        self.file_type = self.file_path.suffix.lower()

    def parse(self) -> dict[str, Any]:
        if not self.file_path.exists():
            raise FileNotFoundError(f"Resume file not found: {self.file_path}")

        if self.file_type == ".txt":
            return self._parse_txt()
        if self.file_type == ".pdf":
            return self._parse_pdf()
        if self.file_type == ".docx":
            return self._parse_docx()
        raise ValueError(f"Unsupported resume type: {self.file_type}")

    def _parse_txt(self) -> dict[str, Any]:
        text = self.file_path.read_text(encoding="utf-8")
        return self._build_result(text, "txt")

    def _parse_pdf(self) -> dict[str, Any]:
        if PdfReader is None:
            raise ImportError("pypdf is required. Install with: pip install pypdf")

        reader = PdfReader(str(self.file_path))
        pages = [page.extract_text() or "" for page in reader.pages]
        text = "\n".join(pages)
        return self._build_result(text, "pdf")

    def _parse_docx(self) -> dict[str, Any]:
        if Document is None:
            raise ImportError("python-docx is required. Install with: pip install python-docx")

        doc = Document(str(self.file_path))
        text = "\n".join(paragraph.text for paragraph in doc.paragraphs)
        return self._build_result(text, "docx")

    def _build_result(self, text: str, format_name: str) -> dict[str, Any]:
        return {
            "format": format_name,
            "raw_text": text,
            "skills": self._extract_skills(text),
            "experience_years": self._estimate_experience(text),
            "education": self._extract_education(text),
            "projects": self._extract_projects(text),
            "sections": self._extract_sections(text),
        }

    def _extract_skills(self, text: str) -> list[str]:
        lower_text = text.lower()

        common_skills = [
            "python",
            "javascript",
            "typescript",
            "java",
            "c++",
            "go",
            "rust",
            "sql",
            "postgres",
            "mysql",
            "mongodb",
            "redis",
            "aws",
            "azure",
            "gcp",
            "docker",
            "kubernetes",
            "terraform",
            "git",
            "ci/cd",
            "github actions",
            "fastapi",
            "flask",
            "django",
            "react",
            "node.js",
            "nodejs",
            "rest api",
            "graphql",
            "machine learning",
            "deep learning",
            "pytorch",
            "tensorflow",
            "power bi",
            "tableau",
            "excel",
            "devops",
            "system design",
            "apis",
        ]

        found = []
        for skill in common_skills:
            if skill in lower_text:
                found.append(skill)
        return found

    def _estimate_experience(self, text: str) -> int:
        patterns = [
            r"(\d+)\s*\+\s*years?",
            r"(\d+)\s*years?\s*of\s*experience",
            r"(\d+)\s*years?",
        ]
        values = []
        for pattern in patterns:
            matches = re.findall(pattern, text.lower())
            for match in matches:
                try:
                    values.append(int(match))
                except ValueError:
                    continue

        if values:
            return max(values)
        return 0

    def _extract_education(self, text: str) -> list[str]:
        education_patterns = [
            r"b\.?s\.?[a-zA-Z\s]*",
            r"m\.?s\.?[a-zA-Z\s]*",
            r"bachelor(?:'s)?",
            r"master(?:'s)?",
            r"phd",
            r"certif(?:ication|ied)",
        ]
        matches = []
        for pattern in education_patterns:
            for m in re.finditer(pattern, text, flags=re.IGNORECASE):
                matches.append(m.group(0).strip())
        return matches[:10]

    def _extract_projects(self, text: str) -> list[str]:
        lines = text.splitlines()
        projects = []
        for line in lines:
            if "project" in line.lower() or "portfolio" in line.lower():
                projects.append(line.strip())
        return projects[:10]

    def _extract_sections(self, text: str) -> dict[str, bool]:
        headers = [
            "experience",
            "education",
            "skills",
            "projects",
            "certifications",
            "summary",
            "achievements",
        ]
        found = {}
        lower_text = text.lower()
        for header in headers:
            found[header] = header in lower_text
        return found
