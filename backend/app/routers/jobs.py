from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Job, JobStatus, Log, Campaign
from app.schemas import JobResponse, LogResponse, ManualTrigger

router = APIRouter()


@router.get("/jobs", response_model=list[JobResponse])
async def list_jobs(
    campaign_id: UUID | None = None,
    status: JobStatus | None = None,
    limit: int = Query(50, le=200),
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    query = select(Job).order_by(Job.scheduled_time.desc()).limit(limit).offset(offset)
    if campaign_id:
        query = query.where(Job.campaign_id == campaign_id)
    if status:
        query = query.where(Job.status == status)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/logs", response_model=list[LogResponse])
async def list_logs(
    job_id: UUID | None = None,
    limit: int = Query(50, le=200),
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    query = select(Log).order_by(Log.created_at.desc()).limit(limit).offset(offset)
    if job_id:
        query = query.where(Log.job_id == job_id)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/trigger")
async def manual_trigger(data: ManualTrigger, db: AsyncSession = Depends(get_db)):
    campaign = await db.get(Campaign, data.campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    from app.tasks.worker import execute_job
    from app.services.campaign_service import create_immediate_job

    job = await create_immediate_job(db, campaign)
    execute_job.delay(str(job.id))
    return {"detail": "Job triggered", "job_id": str(job.id)}
