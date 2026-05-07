from __future__ import annotations

import json
from typing import Any

from app.core.config import settings


async def chat_json(payload: dict[str, Any], fallback: dict[str, Any]) -> dict[str, Any]:
    if not settings.openai_api_key:
        return fallback

    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=settings.openai_api_key)
        response = await client.responses.create(
            model=settings.openai_model,
            input=[
                {
                    "role": "system",
                    "content": (
                        "You are a careful job-search assistant. Return valid JSON only, "
                        "with no markdown fences."
                    ),
                },
                {"role": "user", "content": json.dumps(payload)},
            ],
            temperature=0.2,
        )
        text = response.output_text.strip()
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        return fallback
    return fallback
