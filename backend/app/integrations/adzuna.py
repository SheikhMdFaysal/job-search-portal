from __future__ import annotations

from app.core.config import settings
from app.schemas import JobIn


async def fetch_adzuna_jobs(keyword: str, location: str) -> list[JobIn]:
    if not settings.adzuna_app_id or not settings.adzuna_app_key:
        return []
    import httpx

    url = "https://api.adzuna.com/v1/api/jobs/us/search/1"
    params = {
        "app_id": settings.adzuna_app_id,
        "app_key": settings.adzuna_app_key,
        "what": keyword,
        "where": location,
        "results_per_page": 20,
        "sort_by": "date",
    }
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
    jobs = []
    for item in response.json().get("results", []):
        jobs.append(
            JobIn(
                source="adzuna",
                source_id=str(item.get("id")),
                title=item.get("title") or "Untitled role",
                company=(item.get("company") or {}).get("display_name") or "Unknown company",
                location=(item.get("location") or {}).get("display_name"),
                description=item.get("description") or "",
                salary_min=item.get("salary_min"),
                salary_max=item.get("salary_max"),
                posted_at=item.get("created"),
                url=item.get("redirect_url") or "",
                raw_json=item,
            )
        )
    return jobs
