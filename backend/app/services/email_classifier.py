from __future__ import annotations

from app.integrations.openai_client import chat_json


async def classify_email(subject: str, snippet: str) -> dict[str, str]:
    lowered = f"{subject} {snippet}".lower()
    fallback = {"classification": "Other", "summary": snippet[:240] or subject}
    if "interview" in lowered or "schedule" in lowered:
        fallback["classification"] = "Interview Invite"
    elif "unfortunately" in lowered or "not moving forward" in lowered:
        fallback["classification"] = "Rejection"
    elif "offer" in lowered:
        fallback["classification"] = "Offer"
    elif "received your application" in lowered or "thank you for applying" in lowered:
        fallback["classification"] = "Acknowledgment"
    return await chat_json(
        {
            "subject": subject,
            "snippet": snippet,
            "labels": ["Acknowledgment", "Interview Invite", "Rejection", "Offer", "Other"],
            "instructions": "Return JSON with classification and one-sentence summary.",
        },
        fallback=fallback,
    )
