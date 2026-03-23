from datetime import date, datetime
from zoneinfo import ZoneInfo
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.config import settings

DUTCH_TZ = ZoneInfo("Europe/Amsterdam")
from app.models import Campaign, Job, JobStatus, CampaignStatus
from app.utils.randomizer import generate_random_times, pick_random_entry


def get_sync_session() -> Session:
    engine = create_engine(settings.sync_database_url)
    return Session(engine)


def generate_daily_jobs():
    """Called by Celery Beat daily. Generates randomized jobs for all active campaigns."""
    session = get_sync_session()
    today = datetime.now(DUTCH_TZ).date()

    try:
        campaigns = session.execute(
            select(Campaign).where(
                Campaign.status == CampaignStatus.active,
                Campaign.start_date <= today,
                Campaign.end_date >= today,
            )
        ).scalars().all()

        jobs_created = 0

        for campaign in campaigns:
            if not campaign.excel_data:
                continue

            # Check if jobs already exist for today (prevent duplicates on restart)
            existing = session.execute(
                select(Job).where(
                    Job.campaign_id == campaign.id,
                    Job.scheduled_time >= today.isoformat(),
                    Job.scheduled_time < (today.isoformat() + "T23:59:59"),
                )
            ).scalars().all()

            if existing:
                continue

            # Generate random times for today
            times = generate_random_times(today)

            for scheduled_time in times:
                entry = pick_random_entry(campaign.excel_data)
                job = Job(
                    campaign_id=campaign.id,
                    scheduled_time=scheduled_time,
                    status=JobStatus.pending,
                    entry_data=entry,
                )
                session.add(job)
                jobs_created += 1

        # Mark completed campaigns
        expired = session.execute(
            select(Campaign).where(
                Campaign.status == CampaignStatus.active,
                Campaign.end_date < today,
            )
        ).scalars().all()

        for campaign in expired:
            campaign.status = CampaignStatus.completed

        session.commit()
        return jobs_created

    finally:
        session.close()


def get_pending_jobs_for_now() -> list[str]:
    """Get job IDs that are pending and scheduled for now or in the past."""
    session = get_sync_session()
    try:
        now = datetime.now(DUTCH_TZ)
        jobs = session.execute(
            select(Job).where(
                Job.status == JobStatus.pending,
                Job.scheduled_time <= now,
            )
        ).scalars().all()

        job_ids = []
        for job in jobs:
            job.status = JobStatus.queued
            job_ids.append(str(job.id))

        session.commit()
        return job_ids
    finally:
        session.close()
