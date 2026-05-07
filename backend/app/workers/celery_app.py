from __future__ import annotations

from celery import Celery

from app.core.config import settings

celery_app = Celery("job_portal", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.timezone = settings.timezone
celery_app.conf.beat_schedule = {
    "pull-jobs-every-six-hours": {
        "task": "app.workers.tasks.pull_jobs",
        "schedule": 60 * 60 * 6,
    },
    "scan-gmail-every-hour": {
        "task": "app.workers.tasks.scan_gmail",
        "schedule": 60 * 60,
    },
}
