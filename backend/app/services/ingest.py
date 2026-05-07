from __future__ import annotations

from datetime import datetime, timezone
from difflib import SequenceMatcher

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.integrations.adzuna import fetch_adzuna_jobs
from app.integrations.greenhouse import fetch_greenhouse_jobs
from app.integrations.jsearch import fetch_jsearch_jobs
from app.integrations.lever import fetch_lever_jobs
from app.integrations.themuse import fetch_themuse_jobs
from app.integrations.usajobs import fetch_usajobs
from app.models import Job, Profile
from app.schemas import JobIn
from app.services.matching import score_job


def _similar(a: str, b: str) -> float:
    return SequenceMatcher(a=a.lower(), b=b.lower()).ratio()


def upsert_job(db: Session, job_in: JobIn) -> Job:
    existing = None
    if job_in.source_id:
        existing = db.scalar(
            select(Job).where(Job.source == job_in.source, Job.source_id == job_in.source_id)
        )
    if not existing:
        candidates = db.scalars(select(Job).where(Job.company.ilike(job_in.company))).all()
        existing = next(
            (job for job in candidates if _similar(job.title, job_in.title) > 0.88),
            None,
        )

    if existing:
        for key, value in job_in.model_dump().items():
            setattr(existing, key, value)
        return existing

    job = Job(**job_in.model_dump())
    db.add(job)
    return job


async def ingest_all_sources(db: Session, profile: Profile) -> list[Job]:
    preferences = profile.preferences
    keywords = preferences.get("keywords") or profile.target_roles or ["data analyst"]
    locations = profile.locations or ["remote"]
    raw_jobs: list[JobIn] = []
    for keyword in keywords[:5]:
        for location in locations[:5]:
            raw_jobs.extend(await fetch_adzuna_jobs(keyword, location))
            raw_jobs.extend(await fetch_jsearch_jobs(keyword, location))
            raw_jobs.extend(await fetch_themuse_jobs(keyword, location))
            raw_jobs.extend(await fetch_usajobs(keyword, location))
    raw_jobs.extend(await fetch_greenhouse_jobs(preferences.get("greenhouse_boards", [])))
    raw_jobs.extend(await fetch_lever_jobs(preferences.get("lever_boards", [])))

    saved: list[Job] = []
    for job_in in raw_jobs:
        job = upsert_job(db, job_in)
        if job.posted_at is None:
            job.posted_at = datetime.now(timezone.utc)
        result = await score_job(profile, job)
        job.match_score = result.score
        job.match_reasoning = result.reasoning
        saved.append(job)
    db.commit()
    return saved
