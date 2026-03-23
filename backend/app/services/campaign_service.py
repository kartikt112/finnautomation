from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Job, JobStatus, Campaign
from app.utils.randomizer import pick_random_entry


async def create_immediate_job(db: AsyncSession, campaign: Campaign) -> Job:
    """Create a job that runs immediately (for manual triggers)."""
    entry = pick_random_entry(campaign.excel_data)
    job = Job(
        campaign_id=campaign.id,
        scheduled_time=datetime.utcnow(),
        status=JobStatus.queued,
        entry_data=entry,
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job
