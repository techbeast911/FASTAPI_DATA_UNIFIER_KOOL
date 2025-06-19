
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from uuid import UUID

from src.db.main import get_session # Corrected import for get_session
from sqlalchemy.ext.asyncio import AsyncSession

from src.kool_assembly.schemas.schemas_batteries import BatteryCreate, BatteryRecord, BatteryUpdate
from src.kool_assembly.services.services_batteries import BatteryService


# Initialize the APIRouter for battery-related endpoints

battery_router = APIRouter(
    tags=["Batteries"] # Tags for API documentation (Swagger UI)
)

battery_service = BatteryService()


@battery_router.get("/", response_model=List[BatteryRecord])
async def get_all_batteries(session: AsyncSession = Depends(get_session)) -> List[BatteryRecord]:
    """
    Retrieve a list of all battery records.
    """
    batteries = await battery_service.get_all_batteries(session)
    return batteries


@battery_router.post("/", response_model=BatteryRecord, status_code=status.HTTP_201_CREATED)
async def create_battery(
    battery_data: BatteryCreate,
    session: AsyncSession = Depends(get_session)
) -> BatteryRecord:
    """
    Create a new battery record.
    """
    new_battery = await battery_service.create_battery(battery_data, session)
    return new_battery


@battery_router.get("/{battery_uid}", response_model=BatteryRecord)
async def get_battery_by_uid(
    battery_uid: UUID,
    session: AsyncSession = Depends(get_session)
) -> BatteryRecord:
    """
    Retrieve a single battery record by its unique identifier (UID).
    """
    battery = await battery_service.get_battery_by_uid(battery_uid, session)
    if not battery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Battery with UID '{battery_uid}' not found"
        )
    return battery

@battery_router.get("/serial/{product_serial_number}", response_model=BatteryRecord)
async def get_battery_by_serial_number(
    product_serial_number: str,
    session: AsyncSession = Depends(get_session)
) -> BatteryRecord:
    """
    Retrieve a single battery record by its product serial number.
    """
    battery = await battery_service.get_battery_by_serial_number(product_serial_number, session)
    if not battery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Battery with serial number '{product_serial_number}' not found"
        )
    return battery


@battery_router.patch("/{battery_uid}", response_model=BatteryRecord)
async def update_battery(
    battery_uid: UUID,
    battery_update_data: BatteryUpdate,
    session: AsyncSession = Depends(get_session)
) -> BatteryRecord:
    """
    Update an existing battery record by its UID.
    Partial updates are supported.
    """
    updated_battery = await battery_service.update_battery(battery_uid, battery_update_data, session)
    if not updated_battery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Battery with UID '{battery_uid}' not found"
        )
    return updated_battery


@battery_router.delete("/{battery_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_battery(
    battery_uid: UUID,
    session: AsyncSession = Depends(get_session)
):
    """
    Delete a battery record by its UID.
    Returns 204 No Content on successful deletion.
    """
    was_deleted = await battery_service.delete_battery(battery_uid, session)
    if not was_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Battery with UID '{battery_uid}' not found"
        )
    return None
