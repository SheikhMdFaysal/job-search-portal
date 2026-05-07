from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, HttpUrl

ApplicationStatus = Literal["saved", "applied", "interview", "offer", "rejected", "ghosted"]


class ProfileIn(BaseModel):
    master_resume: dict[str, Any]
    preferences: dict[str, Any] = Field(default_factory=dict)
    target_roles: list[str]
    locations: list[str]
    salary_min: int | None = None
    work_auth_notes: str | None = None


class ProfileOut(ProfileIn):
    id: int
    updated_at: datetime

    model_config = {"from_attributes": True}


class JobIn(BaseModel):
    source: str
    source_id: str | None = None
    title: str
    company: str
    location: str | None = None
    description: str
    salary_min: int | None = None
    salary_max: int | None = None
    posted_at: datetime | None = None
    url: str
    raw_json: dict[str, Any] = Field(default_factory=dict)


class JobOut(JobIn):
    id: int
    match_score: int | None = None
    match_reasoning: str | None = None
    hidden: bool
    created_at: datetime
    application_status: str | None = None

    model_config = {"from_attributes": True}


class ApplicationIn(BaseModel):
    job_id: int
    status: ApplicationStatus = "saved"
    notes: str = ""


class ApplicationUpdate(BaseModel):
    status: ApplicationStatus | None = None
    notes: str | None = None


class ApplicationOut(BaseModel):
    id: int
    job_id: int
    status: str
    applied_at: datetime | None
    resume_doc_path: str | None
    cover_letter_path: str | None
    last_email_at: datetime | None
    notes: str
    job: JobOut

    model_config = {"from_attributes": True}


class UrlCaptureIn(BaseModel):
    url: HttpUrl
    title: str | None = None
    company: str | None = None
    description: str | None = None
    source: str = "manual"


class TailorResponse(BaseModel):
    application_id: int
    document_path: str
    summary: str


class AnalyticsOut(BaseModel):
    status_counts: dict[str, int]
    source_counts: dict[str, int]
    weekly_velocity: list[dict[str, Any]]
    response_rate: float


class CoverLetterIn(BaseModel):
    application_id: int
    tone: str = "warm, concise, and specific"
