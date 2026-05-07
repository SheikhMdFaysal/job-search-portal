from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.database import get_db
from app.integrations.page_metadata import capture_url
from app.models import Application, Document, Job, Profile, User
from app.schemas import (
    AnalyticsOut,
    ApplicationIn,
    ApplicationOut,
    ApplicationUpdate,
    CoverLetterIn,
    JobIn,
    JobOut,
    ProfileIn,
    ProfileOut,
    TailorResponse,
    UrlCaptureIn,
)
from app.services.cover_letter import generate_cover_letter
from app.services.ingest import ingest_all_sources, upsert_job
from app.services.matching import analyze_interview_chance, score_job
from app.services.resume_builder import render_resume_docx, tailor_resume

router = APIRouter()


def get_profile_or_404(db: Session) -> Profile:
    profile = db.scalar(select(Profile).limit(1))
    if not profile:
        raise HTTPException(status_code=404, detail="Complete onboarding first.")
    return profile


def serialize_job(job: Job) -> JobOut:
    data = JobOut.model_validate(job).model_dump()
    data["application_status"] = job.application.status if job.application else None
    return JobOut(**data)


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.put("/profile", response_model=ProfileOut)
def upsert_profile(payload: ProfileIn, db: Session = Depends(get_db)) -> Profile:
    user = db.scalar(select(User).limit(1))
    if not user:
        user = User(email="me@local.jobportal", password_hash="local-only")
        db.add(user)
        db.flush()
    profile = db.scalar(select(Profile).where(Profile.user_id == user.id))
    if not profile:
        profile = Profile(user_id=user.id, **payload.model_dump())
        db.add(profile)
    else:
        for key, value in payload.model_dump().items():
            setattr(profile, key, value)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/profile", response_model=ProfileOut)
def read_profile(db: Session = Depends(get_db)) -> Profile:
    return get_profile_or_404(db)


@router.post("/jobs", response_model=JobOut)
async def create_job(payload: JobIn, db: Session = Depends(get_db)) -> JobOut:
    profile = get_profile_or_404(db)
    job = upsert_job(db, payload)
    result = await score_job(profile, job)
    job.match_score = result.score
    job.match_reasoning = result.reasoning
    db.commit()
    db.refresh(job)
    return serialize_job(job)


@router.post("/jobs/capture-url", response_model=JobOut)
async def capture_job(payload: UrlCaptureIn, db: Session = Depends(get_db)) -> JobOut:
    metadata = await capture_url(payload)
    job_in = JobIn(
        source=payload.source,
        title=metadata["title"],
        company=metadata["company"],
        location=None,
        description=metadata["description"],
        url=metadata["url"],
        raw_json={"captured": True},
    )
    return await create_job(job_in, db)


@router.get("/jobs", response_model=list[JobOut])
def list_jobs(
    status: str | None = None,
    include_hidden: bool = False,
    db: Session = Depends(get_db),
) -> list[JobOut]:
    stmt = select(Job).options(selectinload(Job.application)).order_by(Job.match_score.desc().nullslast())
    if not include_hidden:
        stmt = stmt.where(Job.hidden.is_(False))
    jobs = db.scalars(stmt).all()
    if status:
        jobs = [job for job in jobs if job.application and job.application.status == status]
    return [serialize_job(job) for job in jobs]


@router.get("/jobs/top", response_model=list[JobOut])
def top_jobs(db: Session = Depends(get_db)) -> list[JobOut]:
    jobs = db.scalars(
        select(Job)
        .options(selectinload(Job.application))
        .where(Job.hidden.is_(False))
        .order_by(Job.match_score.desc().nullslast(), Job.created_at.desc())
        .limit(10)
    ).all()
    return [serialize_job(job) for job in jobs]


@router.get("/jobs/{job_id}", response_model=JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)) -> JobOut:
    job = db.scalar(select(Job).options(selectinload(Job.application)).where(Job.id == job_id))
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return serialize_job(job)


@router.post("/jobs/ingest", response_model=dict[str, int])
async def ingest_jobs(db: Session = Depends(get_db)) -> dict[str, int]:
    profile = get_profile_or_404(db)
    jobs = await ingest_all_sources(db, profile)
    return {"ingested": len(jobs)}


@router.get("/jobs/{job_id}/interview-chance")
async def interview_chance(job_id: int, db: Session = Depends(get_db)) -> dict[str, object]:
    profile = get_profile_or_404(db)
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return await analyze_interview_chance(profile, job)


@router.post("/applications", response_model=ApplicationOut)
def create_application(payload: ApplicationIn, db: Session = Depends(get_db)) -> Application:
    job = db.get(Job, payload.job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    application = db.scalar(select(Application).where(Application.job_id == payload.job_id))
    if not application:
        application = Application(job_id=payload.job_id, status=payload.status, notes=payload.notes)
        db.add(application)
    else:
        application.status = payload.status
        application.notes = payload.notes
    if application.status == "applied" and application.applied_at is None:
        application.applied_at = datetime.now(timezone.utc)
    db.commit()
    return db.scalar(
        select(Application)
        .options(selectinload(Application.job).selectinload(Job.application))
        .where(Application.job_id == payload.job_id)
    )


@router.get("/applications", response_model=list[ApplicationOut])
def list_applications(db: Session = Depends(get_db)) -> list[Application]:
    return list(
        db.scalars(
            select(Application)
            .options(selectinload(Application.job).selectinload(Job.application))
            .order_by(Application.updated_at.desc())
        )
    )


@router.patch("/applications/{application_id}", response_model=ApplicationOut)
def update_application(
    application_id: int, payload: ApplicationUpdate, db: Session = Depends(get_db)
) -> Application:
    application = db.get(Application, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    if payload.status:
        application.status = payload.status
        if payload.status == "applied" and application.applied_at is None:
            application.applied_at = datetime.now(timezone.utc)
    if payload.notes is not None:
        application.notes = payload.notes
    db.commit()
    return db.scalar(
        select(Application)
        .options(selectinload(Application.job).selectinload(Job.application))
        .where(Application.id == application_id)
    )


@router.post("/applications/{application_id}/tailor-resume", response_model=TailorResponse)
async def tailor_resume_endpoint(application_id: int, db: Session = Depends(get_db)) -> TailorResponse:
    profile = get_profile_or_404(db)
    application = db.scalar(
        select(Application).options(selectinload(Application.job)).where(Application.id == application_id)
    )
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    tailored = await tailor_resume(profile, application)
    path = render_resume_docx(application, tailored)
    application.resume_doc_path = path
    db.add(Document(type="resume", path=path, related_application_id=application.id))
    db.commit()
    return TailorResponse(
        application_id=application.id,
        document_path=path,
        summary=f"Tailored resume generated for {application.job.company}.",
    )


@router.post("/cover-letter", response_model=TailorResponse)
async def cover_letter(payload: CoverLetterIn, db: Session = Depends(get_db)) -> TailorResponse:
    profile = get_profile_or_404(db)
    application = db.scalar(
        select(Application).options(selectinload(Application.job)).where(Application.id == payload.application_id)
    )
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    path, summary = await generate_cover_letter(profile, application, payload.tone)
    application.cover_letter_path = path
    db.add(Document(type="cover_letter", path=path, related_application_id=application.id))
    db.commit()
    return TailorResponse(application_id=application.id, document_path=path, summary=summary)


@router.get("/analytics", response_model=AnalyticsOut)
def analytics(db: Session = Depends(get_db)) -> AnalyticsOut:
    status_rows = db.execute(select(Application.status, func.count()).group_by(Application.status)).all()
    source_rows = db.execute(select(Job.source, func.count()).group_by(Job.source)).all()
    applied_total = db.scalar(select(func.count()).select_from(Application)) or 0
    responded = db.scalar(
        select(func.count()).select_from(Application).where(Application.status.in_(["interview", "offer", "rejected"]))
    ) or 0
    return AnalyticsOut(
        status_counts={str(status): int(count) for status, count in status_rows},
        source_counts={str(source): int(count) for source, count in source_rows},
        weekly_velocity=[],
        response_rate=round(float(responded) / float(applied_total), 3) if applied_total else 0.0,
    )
