from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.core.database import get_db
from app.models.all_models import CallLog
from app.services.pms.mock_service import MockPMSService

router = APIRouter()

@router.get("/calls")
async def get_calls(db: AsyncSession = Depends(get_db)):
    """Fetch call logs from the database."""
    result = await db.execute(select(CallLog).order_by(CallLog.created_at.desc()))
    calls = result.scalars().all()
    return calls

@router.get("/appointments")
def get_appointments():
    """Fetch available appointment slots from the Mock PMS."""
    # In a real app, this might query the DB or call an external API
    return MockPMSService.get_available_slots()
