# File: src/kool_assembly/routes/routes_iot.py
# -*- coding: utf-8 -*-

from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from uuid import UUID

from src.db.main import get_session
from sqlalchemy.ext.asyncio import AsyncSession

from src.kool_assembly.schemas.schemas_iot import IotCreate, IotRecord, IotUpdate
from src.kool_assembly.services.services_iot import IotService


iot_router = APIRouter(
    tags=["IoT"]
)

iot_service = IotService()

@iot_router.get("/", response_model=List[IotRecord])
async def get_all_iot_records(session: AsyncSession = Depends(get_session)) -> List[IotRecord]:
    """
    Retrieve a list of all IoT records.
    """
    iot_records = await iot_service.get_all_iot(session)
    return iot_records

@iot_router.post("/", response_model=IotRecord, status_code=status.HTTP_201_CREATED)
async def create_iot_record(
    iot_data: IotCreate,
    session: AsyncSession = Depends(get_session),
) -> IotRecord:
    """
    Create a new IoT record.
    """
    new_iot_record = await iot_service.create_iot(iot_data, session)
    return new_iot_record


@iot_router.get("/{iot_uid}", response_model=IotRecord)
async def get_iot_record_by_uid(
    iot_uid: UUID,
    session: AsyncSession = Depends(get_session),
) -> IotRecord:
    """
    Retrieve a single IoT record by its unique identifier (UID).
    """
    iot_record = await iot_service.get_iot_by_uid(iot_uid, session)
    if not iot_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"IoT record with UID '{iot_uid}' not found"
        )
    return iot_record

@iot_router.get("/serial/{product_serial_number}", response_model=IotRecord)
async def get_iot_record_by_product_serial_number(
    product_serial_number: str,
    session: AsyncSession = Depends(get_session),
) -> IotRecord:
    """
    Retrieve a single IoT record by its product serial number.
    """
    iot_record = await iot_service.get_iot_by_product_serial_number(product_serial_number, session)
    if not iot_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"IoT record with serial number '{product_serial_number}' not found"
        )
    return iot_record


@iot_router.patch("/{iot_uid}", response_model=IotRecord)
async def update_iot_record(
    iot_uid: UUID,
    iot_update_data: IotUpdate,
    session: AsyncSession = Depends(get_session),
) -> IotRecord:
    """
    Update an existing IoT record by its UID.
    Partial updates are supported.
    """
    updated_iot_record = await iot_service.update_iot(iot_uid, iot_update_data, session)
    if not updated_iot_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"IoT record with UID '{iot_uid}' not found"
        )
    return updated_iot_record


@iot_router.delete("/{iot_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_iot_record(
    iot_uid: UUID,
    session: AsyncSession = Depends(get_session),
):
    """
    Delete an IoT record by its UID.
    Returns 204 No Content on successful deletion.
    """
    was_deleted = await iot_service.delete_iot(iot_uid, session)
    if not was_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"IoT record with UID '{iot_uid}' not found"
        )
    return None