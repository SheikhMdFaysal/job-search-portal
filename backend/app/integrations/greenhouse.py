from __future__ import annotations

from app.schemas import JobIn


async def fetch_greenhouse_jobs(boards: list[str]) -> list[JobIn]:
    import httpx

    jobs: list[JobIn] = []
    async with httpx.AsyncClient(timeout=20) as client:
        for board in boards:
            response = await client.get(f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs")
            if response.status_code >= 400:
                continue
            for item in response.json().get("jobs", []):
                jobs.append(
                    JobIn(
                        source="greenhouse",
                        source_id=str(item.get("id")),
                        title=item.get("title") or "Untitled role",
                        company=board,
                        location=(item.get("location") or {}).get("name"),
                        description=item.get("content") or "",
                        url=item.get("absolute_url") or "",
                        raw_json=item,
                    )
                )
    return jobs
