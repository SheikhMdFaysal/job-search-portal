from __future__ import annotations

from app.schemas import JobIn


async def fetch_lever_jobs(boards: list[str]) -> list[JobIn]:
    import httpx

    jobs: list[JobIn] = []
    async with httpx.AsyncClient(timeout=20) as client:
        for board in boards:
            response = await client.get(f"https://api.lever.co/v0/postings/{board}", params={"mode": "json"})
            if response.status_code >= 400:
                continue
            for item in response.json():
                jobs.append(
                    JobIn(
                        source="lever",
                        source_id=item.get("id"),
                        title=item.get("text") or "Untitled role",
                        company=board,
                        location=(item.get("categories") or {}).get("location"),
                        description=item.get("descriptionPlain") or item.get("description") or "",
                        url=item.get("hostedUrl") or "",
                        raw_json=item,
                    )
                )
    return jobs
