from __future__ import annotations

import asyncio

from sqlalchemy import select

from app.core.database import SessionLocal
from app.integrations.gmail import fetch_relevant_threads
from app.models import Application, Email, Profile
from app.services.email_classifier import classify_email
from app.services.ingest import ingest_all_sources
from app.workers.celery_app import celery_app


@celery_app.task(name="app.workers.tasks.pull_jobs")
def pull_jobs() -> dict[str, int]:
    async def _run() -> dict[str, int]:
        with SessionLocal() as db:
            profile = db.scalar(select(Profile).limit(1))
            if not profile:
                return {"ingested": 0}
            jobs = await ingest_all_sources(db, profile)
            return {"ingested": len(jobs)}

    return asyncio.run(_run())


@celery_app.task(name="app.workers.tasks.scan_gmail")
def scan_gmail() -> dict[str, int]:
    async def _run() -> dict[str, int]:
        with SessionLocal() as db:
            applications = db.scalars(select(Application)).all()
            company_names = [application.job.company for application in applications]
            messages = await fetch_relevant_threads(company_names)
            updated = 0
            for message in messages:
                application = next(
                    (
                        item
                        for item in applications
                        if item.job.company.lower() in f"{message.sender} {message.subject}".lower()
                    ),
                    None,
                )
                if not application:
                    continue
                result = await classify_email(message.subject, message.snippet)
                db.add(
                    Email(
                        application_id=application.id,
                        gmail_thread_id=message.thread_id,
                        classification=result["classification"],
                        summary=result["summary"],
                        received_at=message.received_at,
                    )
                )
                application.last_email_at = message.received_at
                if result["classification"] == "Interview Invite":
                    application.status = "interview"
                elif result["classification"] == "Offer":
                    application.status = "offer"
                elif result["classification"] == "Rejection":
                    application.status = "rejected"
                updated += 1
            db.commit()
            return {"updated": updated}

    return asyncio.run(_run())
