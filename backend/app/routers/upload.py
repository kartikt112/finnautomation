from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, timedelta
import uuid
import aiofiles

from app.database import get_db
from app.models import Campaign, Client, CampaignStatus
from app.schemas import CampaignResponse
from app.services.excel_service import parse_excel
from app.config import settings

router = APIRouter()


@router.post("/upload", response_model=CampaignResponse)
async def upload_excel(
    file: UploadFile = File(...),
    client_id: UUID = Form(...),
    name: str = Form(...),
    target_url: str = Form(...),
    duration_days: int = Form(30),
    db: AsyncSession = Depends(get_db),
):
    client = await db.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    if not file.filename.endswith((".xlsx", ".xls", ".csv")):
        raise HTTPException(status_code=400, detail="Only .xlsx or .csv files are accepted")

    # Save file
    file_id = str(uuid.uuid4())
    file_path = settings.upload_path / f"{file_id}_{file.filename}"
    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    # Parse Excel
    try:
        excel_data = parse_excel(str(file_path))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not excel_data:
        raise HTTPException(status_code=400, detail="Excel file is empty")

    # Create campaign
    start = date.today()
    campaign = Campaign(
        client_id=client_id,
        name=name,
        target_url=target_url,
        excel_file_path=str(file_path),
        excel_data=excel_data,
        duration_days=duration_days,
        start_date=start,
        end_date=start + timedelta(days=duration_days),
        status=CampaignStatus.active,
    )
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    return campaign
