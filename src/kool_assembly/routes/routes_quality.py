# File: src/kool_assembly/routes/routes_quality.py
# -*- coding: utf-8 -*-
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from uuid import UUID

from src.db.main import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from src.kool_assembly.schemas.schemas_quality import QualityCreate, QualityRecord, QualityUpdate
from src.kool_assembly.services.services_quality import QualityServices

quality_router = APIRouter(
    tags=["Quality"]
)

quality_service = QualityServices()

@quality_router.get("/", response_model=List[QualityRecord])
async def get_all_quality_records(session: AsyncSession = Depends(get_session)) -> List[QualityRecord]:
    """
    Retrieve a list of all Quality records.
    """
    quality_records = await quality_service.get_all_quality(session)
    return quality_records

@quality_router.post("/", response_model=QualityRecord, status_code=status.HTTP_201_CREATED)
async def create_quality_record(
    quality_data: QualityCreate,
    session: AsyncSession = Depends(get_session),
) -> QualityRecord:
    """
    Create a new Quality record.
    """
    new_quality_record = await quality_service.create_quality(quality_data, session)
    return new_quality_record


@quality_router.get("/{quality_uid}", response_model=QualityRecord)
async def get_quality_record_by_uid(
    quality_uid: UUID,
    session: AsyncSession = Depends(get_session),
) -> QualityRecord:
    """
    Retrieve a single Quality record by its unique identifier (UID).
    """
    quality_record = await quality_service.get_quality_by_uid(quality_uid, session)
    if not quality_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quality record with UID '{quality_uid}' not found"
        )
    return quality_record

@quality_router.get("/serial/{product_serial_number}", response_model=QualityRecord)
async def get_quality_record_by_product_serial_number(
    product_serial_number: str,
    session: AsyncSession = Depends(get_session),
) -> QualityRecord:
    """
    Retrieve a single Quality record by its product serial number.
    """
    quality_record = await quality_service.get_quality_by_product_serial_number(product_serial_number, session)
    if not quality_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quality record with serial number '{product_serial_number}' not found"
        )
    return quality_record


@quality_router.patch("/{quality_uid}", response_model=QualityRecord)
async def update_quality_record(
    quality_uid: UUID,
    quality_update_data: QualityUpdate,
    session: AsyncSession = Depends(get_session),
) -> QualityRecord:
    """
    Update an existing Quality record by its UID.
    Partial updates are supported.
    """
    updated_quality_record = await quality_service.update_quality(quality_uid, quality_update_data, session)
    if not updated_quality_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quality record with UID '{quality_uid}' not found"
        )
    return updated_quality_record


@quality_router.delete("/{quality_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quality_record(
    quality_uid: UUID,
    session: AsyncSession = Depends(get_session),
):
    """
    Delete a Quality record by its UID.
    Returns 204 No Content on successful deletion.
    """
    was_deleted = await quality_service.delete_quality(quality_uid, session)
    if not was_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quality record with UID '{quality_uid}' not found"
        )
    return None
