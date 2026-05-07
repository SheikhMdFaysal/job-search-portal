from __future__ import annotations

from datetime import datetime, timezone

from app.core.database import SessionLocal
from app.models import Job
from app.schemas import JobIn, ProfileIn
from app.api.routes import upsert_job


PROFILE = ProfileIn(
    master_resume={
        "name": "Sheikh Md Faysal",
        "headline": "Business analytics and data analytics candidate",
        "skills": ["SQL", "Python", "Excel", "Power BI", "Tableau", "financial analysis", "dashboarding"],
        "experience": [
            {
                "role": "Graduate Assistant / Analytics Projects",
                "company": "Academic and project work",
                "bullets": [
                    "Built dashboards and reports to summarize operational and financial datasets.",
                    "Prepared stakeholder-ready analysis using Excel, SQL, and visualization tools.",
                ],
            }
        ],
        "education": [{"degree": "Graduate study in business/data analytics", "school": "Montclair State University"}],
        "certifications": [],
    },
    preferences={
        "keywords": ["data analyst", "business analyst", "financial analyst"],
        "greenhouse_boards": [],
        "lever_boards": [],
    },
    target_roles=["data analyst", "business analyst", "financial analyst"],
    locations=["Jersey City NJ", "New York NY", "Remote US"],
    salary_min=65000,
    work_auth_notes="Update with current work authorization details.",
)


JOBS = [
    JobIn(
        source="seed",
        source_id="seed-1",
        title="Junior Data Analyst",
        company="Northstar Analytics",
        location="New York NY",
        description="SQL, Excel, Tableau, dashboarding, stakeholder reporting, and data quality analysis.",
        salary_min=70000,
        salary_max=85000,
        posted_at=datetime.now(timezone.utc),
        url="https://example.com/jobs/1",
        raw_json={"seed": True},
    ),
    JobIn(
        source="seed",
        source_id="seed-2",
        title="Business Analyst - Finance",
        company="Hudson Markets",
        location="Jersey City NJ",
        description="Finance analytics role using Excel, Power BI, forecasting, data modeling, and executive reporting.",
        salary_min=75000,
        salary_max=92000,
        posted_at=datetime.now(timezone.utc),
        url="https://example.com/jobs/2",
        raw_json={"seed": True},
    ),
]


def main() -> None:
    from app.api.routes import upsert_profile

    with SessionLocal() as db:
        upsert_profile(PROFILE, db)
        for job in JOBS:
            saved = upsert_job(db, job)
            saved.match_score = 86 if saved.title.startswith("Junior") else 91
            saved.match_reasoning = "Seeded role matches analytics, reporting, and location preferences."
        db.commit()
        print(f"Seeded {len(JOBS)} jobs.")


if __name__ == "__main__":
    main()
