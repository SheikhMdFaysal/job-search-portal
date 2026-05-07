from __future__ import annotations

from pathlib import Path

from docx import Document as DocxDocument
from docx.shared import Pt

from app.core.config import settings
from app.integrations.openai_client import chat_json
from app.models import Application, Profile
from app.services.resume_builder import _safe_slug


async def generate_cover_letter(profile: Profile, application: Application, tone: str) -> tuple[str, str]:
    job = application.job
    fallback_body = (
        f"Dear Hiring Team,\n\n"
        f"I am excited to apply for the {job.title} role at {job.company}. "
        "My background in analytics, reporting, and stakeholder communication aligns well with the needs described in this position.\n\n"
        "I would welcome the opportunity to discuss how my experience can support your team.\n\n"
        "Sincerely,\nSheikh Md Faysal"
    )
    result = await chat_json(
        {
            "profile": profile.master_resume,
            "job": {"title": job.title, "company": job.company, "description": job.description[:8000]},
            "tone": tone,
            "instructions": "Return JSON with keys body and positioning_summary. Do not invent facts.",
        },
        fallback={"body": fallback_body, "positioning_summary": "Uses a concise analytics-focused angle."},
    )

    storage = Path(settings.document_storage_dir)
    storage.mkdir(parents=True, exist_ok=True)
    path = storage / f"{application.id}-{_safe_slug(job.company)}-{_safe_slug(job.title)}-cover-letter.docx"
    doc = DocxDocument()
    doc.styles["Normal"].font.name = "Calibri"
    doc.styles["Normal"].font.size = Pt(11)
    for paragraph in str(result["body"]).split("\n\n"):
        doc.add_paragraph(paragraph)
    doc.save(path)
    return str(path), str(result.get("positioning_summary", "Cover letter generated."))
