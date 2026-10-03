from __future__ import annotations

import json
from datetime import datetime

from app.database.models import JobApplication, CandidateProfile, get_session


class JobApplicationDB:
    @staticmethod
    def save_application(data: dict) -> JobApplication:
        session = get_session()
        try:
            app = JobApplication(**data)
            session.add(app)
            session.commit()
            session.refresh(app)
            return app
        finally:
            session.close()

    @staticmethod
    def get_all() -> list[JobApplication]:
        session = get_session()
        try:
            return session.query(JobApplication).all()
        finally:
            session.close()

    @staticmethod
    def get_by_status(status: str) -> list[JobApplication]:
        session = get_session()
        try:
            return session.query(JobApplication).filter(JobApplication.status == status).all()
        finally:
            session.close()

    @staticmethod
    def update_status(app_id: int, status: str, notes: str | None = None) -> JobApplication | None:
        session = get_session()
        try:
            app = session.query(JobApplication).filter(JobApplication.id == app_id).first()
            if app is None:
                return None

            app.status = status
            if notes:
                app.notes = notes
            if status == "applied" and app.applied_at is None:
                app.applied_at = datetime.utcnow()

            session.commit()
            session.refresh(app)
            return app
        finally:
            session.close()

    @staticmethod
    def get_stats() -> dict:
        session = get_session()
        try:
            total = session.query(JobApplication).count()
            applied = session.query(JobApplication).filter(JobApplication.status == "applied").count()
            interview = session.query(JobApplication).filter(JobApplication.status == "interview").count()
            rejected = session.query(JobApplication).filter(JobApplication.status == "rejected").count()
            offers = session.query(JobApplication).filter(JobApplication.status == "offer").count()

            return {
                "total": total,
                "applied": applied,
                "interview": interview,
                "rejected": rejected,
                "offer": offers,
            }
        finally:
            session.close()


class CandidateProfileDB:
    @staticmethod
    def save_profile(data: dict) -> CandidateProfile:
        session = get_session()
        try:
            profile = CandidateProfile(**data)
            session.add(profile)
            session.commit()
            session.refresh(profile)
            return profile
        finally:
            session.close()

    @staticmethod
    def get_latest() -> CandidateProfile | None:
        session = get_session()
        try:
            return session.query(CandidateProfile).order_by(CandidateProfile.id.desc()).first()
        finally:
            session.close()
