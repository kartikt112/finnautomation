from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from datetime import date, datetime

from app.database import get_db
from app.models import Campaign, Job, JobStatus, CampaignStatus, Client
from app.schemas import CampaignResponse, CampaignDetail, DashboardStats

router = APIRouter()


@router.get("/campaigns", response_model=list[CampaignResponse])
async def list_campaigns(
    status: CampaignStatus | None = None,
    client_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Campaign).order_by(Campaign.created_at.desc())
    if status:
        query = query.where(Campaign.status == status)
    if client_id:
        query = query.where(Campaign.client_id == client_id)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/campaigns/{campaign_id}", response_model=CampaignDetail)
async def get_campaign(campaign_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Campaign)
        .options(selectinload(Campaign.client), selectinload(Campaign.jobs))
        .where(Campaign.id == campaign_id)
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    total = len(campaign.jobs)
    successful = sum(1 for j in campaign.jobs if j.status == JobStatus.success)
    failed = sum(1 for j in campaign.jobs if j.status == JobStatus.failed)

    return CampaignDetail(
        **{c.key: getattr(campaign, c.key) for c in Campaign.__table__.columns},
        client=campaign.client,
        jobs=sorted(campaign.jobs, key=lambda j: j.scheduled_time, reverse=True)[:50],
        total_jobs=total,
        successful_jobs=successful,
        failed_jobs=failed,
    )


@router.post("/campaigns/{campaign_id}/pause")
async def pause_campaign(campaign_id: UUID, db: AsyncSession = Depends(get_db)):
    campaign = await db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    campaign.status = CampaignStatus.paused
    await db.commit()
    return {"detail": "Campaign paused"}


@router.post("/campaigns/{campaign_id}/resume")
async def resume_campaign(campaign_id: UUID, db: AsyncSession = Depends(get_db)):
    campaign = await db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if campaign.end_date < date.today():
        raise HTTPException(status_code=400, detail="Campaign has ended")
    campaign.status = CampaignStatus.active
    await db.commit()
    return {"detail": "Campaign resumed"}


@router.get("/dashboard/stats", response_model=DashboardStats)
async def dashboard_stats(db: AsyncSession = Depends(get_db)):
    today = date.today()
    today_start = datetime(today.year, today.month, today.day)
    today_end = datetime(today.year, today.month, today.day, 23, 59, 59)

    total_clients = (await db.execute(select(func.count(Client.id)))).scalar() or 0
    active_campaigns = (
        await db.execute(
            select(func.count(Campaign.id)).where(Campaign.status == CampaignStatus.active)
        )
    ).scalar() or 0

    todays_jobs_q = select(Job).where(Job.scheduled_time.between(today_start, today_end))
    todays_jobs_result = await db.execute(todays_jobs_q)
    todays_jobs = todays_jobs_result.scalars().all()

    total_today = len(todays_jobs)
    successful_today = sum(1 for j in todays_jobs if j.status == JobStatus.success)
    failed_today = sum(1 for j in todays_jobs if j.status == JobStatus.failed)
    success_rate = (successful_today / total_today * 100) if total_today > 0 else 0.0

    return DashboardStats(
        total_clients=total_clients,
        active_campaigns=active_campaigns,
        todays_jobs=total_today,
        success_rate=round(success_rate, 1),
        total_jobs_today=total_today,
        successful_today=successful_today,
        failed_today=failed_today,
    )
