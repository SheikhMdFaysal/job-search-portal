from __future__ import annotations

import re

from app.schemas import UrlCaptureIn


async def capture_url(payload: UrlCaptureIn) -> dict[str, str]:
    if payload.title and payload.company and payload.description:
        return {
            "title": payload.title,
            "company": payload.company,
            "description": payload.description,
            "url": str(payload.url),
        }

    import httpx

    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
        response = await client.get(str(payload.url), headers={"User-Agent": "PersonalJobPortal/0.1"})
        response.raise_for_status()
    html = response.text

    def meta(name: str) -> str | None:
        patterns = [
            rf'<meta[^>]+property=["\']{re.escape(name)}["\'][^>]+content=["\']([^"\']+)',
            rf'<meta[^>]+name=["\']{re.escape(name)}["\'][^>]+content=["\']([^"\']+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                return re.sub(r"\s+", " ", match.group(1)).strip()
        return None

    title = payload.title or meta("og:title") or re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
    title_text = title.group(1).strip() if hasattr(title, "group") else str(title or "Captured job")
    description = payload.description or meta("og:description") or meta("description") or title_text
    return {
        "title": title_text,
        "company": payload.company or "Unknown company",
        "description": description,
        "url": str(payload.url),
    }
