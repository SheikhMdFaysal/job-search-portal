from __future__ import annotations

from app.schemas import JobIn


async def fetch_themuse_jobs(keyword: str, location: str) -> list[JobIn]:
    import httpx

    params = {"page": 1, "category": keyword, "location": location}
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get("https://www.themuse.com/api/public/jobs", params=params)
        if response.status_code >= 400:
            return []
    jobs = []
    for item in response.json().get("results", []):
        company = (item.get("company") or {}).get("name") or "Unknown company"
        locations = ", ".join(loc.get("name", "") for loc in item.get("locations", []))
        jobs.append(
            JobIn(
                source="themuse",
                source_id=str(item.get("id")),
                title=item.get("name") or "Untitled role",
                company=company,
                location=locations or None,
                description=item.get("contents") or "",
                url=item.get("refs", {}).get("landing_page") or "",
                raw_json=item,
            )
        )
    return jobs
