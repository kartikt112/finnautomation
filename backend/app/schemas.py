from pydantic import BaseModel, HttpUrl
from datetime import datetime, date
from uuid import UUID
from typing import Optional
from app.models import CampaignStatus, JobStatus


# --- Client ---
class ClientCreate(BaseModel):
    name: str
    multilogin_profile_group: Optional[str] = None


class ClientResponse(BaseModel):
    id: UUID
    name: str
    multilogin_profile_group: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# --- Campaign ---
class CampaignCreate(BaseModel):
    client_id: UUID
    name: str
    target_url: str
    duration_days: int = 30


class CampaignResponse(BaseModel):
    id: UUID
    client_id: UUID
    name: str
    target_url: str
    excel_file_path: Optional[str]
    duration_days: int
    start_date: date
    end_date: date
    status: CampaignStatus
    created_at: datetime

    class Config:
        from_attributes = True


class CampaignDetail(CampaignResponse):
    client: ClientResponse
    jobs: list["JobResponse"] = []
    total_jobs: int = 0
    successful_jobs: int = 0
    failed_jobs: int = 0


# --- Job ---
class JobResponse(BaseModel):
    id: UUID
    campaign_id: UUID
    scheduled_time: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    status: JobStatus
    retry_count: int
    entry_data: Optional[dict]
    error_message: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# --- Log ---
class LogResponse(BaseModel):
    id: UUID
    job_id: UUID
    status: str
    message: Optional[str]
    error_trace: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# --- Dashboard ---
class DashboardStats(BaseModel):
    total_clients: int
    active_campaigns: int
    todays_jobs: int
    success_rate: float
    total_jobs_today: int
    successful_today: int
    failed_today: int


# --- Trigger ---
class ManualTrigger(BaseModel):
    campaign_id: UUID
