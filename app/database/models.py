from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class JobApplication(Base):
    __tablename__ = "job_applications"

    id = Column(Integer, primary_key=True)
    job_title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    location = Column(String(255), nullable=True)
    job_url = Column(String(500), nullable=True)
    source = Column(String(100), default="manual")
    description = Column(Text, nullable=True)
    salary = Column(String(200), nullable=True)
    status = Column(String(100), default="discovered")
    match_score = Column(Float, default=0.0)
    matched_skills = Column(Text, nullable=True)
    missing_skills = Column(Text, nullable=True)
    cover_letter = Column(Text, nullable=True)
    tailored_resume = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    discovered_at = Column(DateTime, default=datetime.utcnow)
    applied_at = Column(DateTime, nullable=True)
    follow_up_date = Column(DateTime, nullable=True)
    interview_date = Column(DateTime, nullable=True)


class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    resume_path = Column(String(500), nullable=True)
    skills = Column(Text, nullable=True)
    years_experience = Column(Integer, default=0)
    preferred_locations = Column(Text, nullable=True)
    preferred_roles = Column(Text, nullable=True)
    min_salary = Column(Integer, default=0)
    max_salary = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def get_database_url() -> str:
    import os
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url
    return "sqlite:///job_applications.db"


def init_database() -> None:
    engine = create_engine(get_database_url())
    Base.metadata.create_all(bind=engine)
    print(f"Database initialized: {get_database_url()}")


def get_session():
    engine = create_engine(get_database_url())
    Session = sessionmaker(bind=engine)
    return Session()
