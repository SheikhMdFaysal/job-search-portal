from __future__ import annotations

from app.core.config import settings
from app.schemas import JobIn


async def fetch_jsearch_jobs(keyword: str, location: str) -> list[JobIn]:
    if not settings.rapidapi_key:
        return []
    import httpx

    headers = {
        "X-RapidAPI-Key": settings.rapidapi_key,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
    }
    params = {"query": f"{keyword} in {location}", "page": "1", "num_pages": "1"}
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get("https://jsearch.p.rapidapi.com/search", headers=headers, params=params)
        response.raise_for_status()
    jobs = []
    for item in response.json().get("data", []):
        jobs.append(
            JobIn(
                source="jsearch",
                source_id=item.get("job_id"),
                title=item.get("job_title") or "Untitled role",
                company=item.get("employer_name") or "Unknown company",
                location=item.get("job_city") or item.get("job_country"),
                description=item.get("job_description") or "",
                salary_min=item.get("job_min_salary"),
                salary_max=item.get("job_max_salary"),
                posted_at=None,
                url=item.get("job_apply_link") or item.get("job_google_link") or "",
                raw_json=item,
            )
        )
    return jobs
