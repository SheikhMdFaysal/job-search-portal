from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class GmailMessage:
    thread_id: str
    sender: str
    subject: str
    snippet: str
    received_at: datetime


async def fetch_relevant_threads(company_names: list[str]) -> list[GmailMessage]:
    # OAuth setup is intentionally explicit in README. This placeholder keeps the
    # worker contract stable while credentials are not configured.
    return []
