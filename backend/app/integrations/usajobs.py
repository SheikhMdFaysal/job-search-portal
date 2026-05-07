from __future__ import annotations

from app.core.config import settings
from app.schemas import JobIn


async def fetch_usajobs(keyword: str, location: str) -> list[JobIn]:
    if not settings.usajobs_api_key or not settings.usajobs_user_agent:
        return []
    import httpx

    headers = {
        "Host": "data.usajobs.gov",
        "User-Agent": settings.usajobs_user_agent,
        "Authorization-Key": settings.usajobs_api_key,
    }
    params = {"Keyword": keyword, "LocationName": location, "ResultsPerPage": 20}
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get("https://data.usajobs.gov/api/search", headers=headers, params=params)
        response.raise_for_status()
    jobs = []
    for item in response.json().get("SearchResult", {}).get("SearchResultItems", []):
        detail = item.get("MatchedObjectDescriptor", {})
        jobs.append(
            JobIn(
                source="usajobs",
                source_id=detail.get("PositionID"),
                title=detail.get("PositionTitle") or "Untitled role",
                company=detail.get("OrganizationName") or "Federal agency",
                location=", ".join(loc.get("LocationName", "") for loc in detail.get("PositionLocation", [])),
                description=detail.get("UserArea", {}).get("Details", {}).get("JobSummary") or "",
                salary_min=None,
                salary_max=None,
                posted_at=None,
                url=detail.get("PositionURI") or "",
                raw_json=detail,
            )
        )
    return jobs
