from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from app.integrations.openai_client import chat_json
from app.models import Job, Profile


@dataclass(frozen=True)
class MatchResult:
    score: int
    reasoning: str


IMPORTANT_TERMS = {
    "sql",
    "python",
    "excel",
    "tableau",
    "power bi",
    "analytics",
    "data",
    "finance",
    "stakeholder",
    "reporting",
    "dashboard",
    "forecast",
    "modeling",
    "etl",
}


def keyword_score(profile: Profile, job: Job) -> MatchResult:
    profile_text = json.dumps(profile.master_resume).lower() + " " + " ".join(profile.target_roles).lower()
    job_text = f"{job.title} {job.company} {job.description}".lower()
    matched = sorted(term for term in IMPORTANT_TERMS if term in profile_text and term in job_text)
    role_bonus = 15 if any(role.lower() in job_text for role in profile.target_roles) else 0
    location_bonus = 10 if any(loc.lower() in (job.location or "").lower() for loc in profile.locations) else 0
    base = min(75, len(matched) * 8)
    score = max(35, min(100, base + role_bonus + location_bonus))
    reason = (
        f"Matched {len(matched)} relevant terms"
        + (f": {', '.join(matched[:7])}" if matched else " from the current profile")
        + "."
    )
    return MatchResult(score=score, reasoning=reason)


async def score_job(profile: Profile, job: Job) -> MatchResult:
    fallback = keyword_score(profile, job)
    prompt = {
        "profile": profile.master_resume,
        "preferences": profile.preferences,
        "target_roles": profile.target_roles,
        "locations": profile.locations,
        "job": {
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "description": re.sub(r"\s+", " ", job.description)[:8000],
        },
        "instructions": (
            "Return JSON with integer score 0-100 and a one-sentence reasoning. "
            "Prioritize skill match, role fit, location, salary, and likely sponsorship/work authorization fit."
        ),
    }
    result = await chat_json(prompt, fallback={"score": fallback.score, "reasoning": fallback.reasoning})
    return MatchResult(score=int(result["score"]), reasoning=str(result["reasoning"]))


async def analyze_interview_chance(profile: Profile, job: Job) -> dict[str, Any]:
    fallback = keyword_score(profile, job)
    job_words = set(re.findall(r"[a-zA-Z][a-zA-Z+#.]{2,}", job.description.lower()))
    profile_text = json.dumps(profile.master_resume).lower()
    missing = sorted(term for term in IMPORTANT_TERMS if term in job_words and term not in profile_text)
    return await chat_json(
        {
            "profile": profile.master_resume,
            "job": {"title": job.title, "company": job.company, "description": job.description[:8000]},
            "instructions": (
                "Return JSON with keyword_match_percentage, missing_critical_keywords, "
                "suggested_resume_edits, cover_letter_angles, callback_probability_estimate, reasoning. "
                "Label probability as an estimate, not a promise."
            ),
        },
        fallback={
            "keyword_match_percentage": fallback.score,
            "missing_critical_keywords": missing[:10],
            "suggested_resume_edits": ["Add measurable impact bullets that mirror the strongest job keywords."],
            "cover_letter_angles": ["Connect analytics work to the company's business problem."],
            "callback_probability_estimate": max(5, min(65, fallback.score - 25)),
            "reasoning": fallback.reasoning,
        },
    )
