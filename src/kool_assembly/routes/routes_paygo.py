
# File: src/kool_assembly/routes/routes_paygo.py
# -*- coding: utf-8 -*-
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from uuid import UUID

from src.db.main import get_session
from sqlalchemy.ext.asyncio import AsyncSession

from src.kool_assembly.schemas.schemas_paygo import PaygoCreate, PaygoRecords, PaygoUpdate
from src.kool_assembly.services.services_paygo import PaygoService

paygo_router = APIRouter(
    tags=["Paygo"]
)

paygo_service = PaygoService()

@paygo_router.get("/", response_model=List[PaygoRecords])
async def get_all_paygo_records(session: AsyncSession = Depends(get_session)) -> List[PaygoRecords]:
    """
    Retrieve a list of all Paygo records.
    """
    paygo_records = await paygo_service.get_all_paygo(session)
    return paygo_records

@paygo_router.post("/", response_model=PaygoRecords, status_code=status.HTTP_201_CREATED)
async def create_paygo_record(
    paygo_data: PaygoCreate,
    session: AsyncSession = Depends(get_session),
) -> PaygoRecords:
    """
    Create a new Paygo record.
    """
    new_paygo_record = await paygo_service.create_paygo(paygo_data, session)
    return new_paygo_record


@paygo_router.get("/{paygo_uid}", response_model=PaygoRecords)
async def get_paygo_record_by_uid(
    paygo_uid: UUID,
    session: AsyncSession = Depends(get_session),
) -> PaygoRecords:
    """
    Retrieve a single Paygo record by its unique identifier (UID).
    """
    paygo_record = await paygo_service.get_paygo_by_uid(paygo_uid, session)
    if not paygo_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paygo record with UID '{paygo_uid}' not found"
        )
    return paygo_record

# FIX: Changed path back to /serial/{product_serial_number} and
#      updated parameter name and service call
@paygo_router.get("/serial/{product_serial_number}", response_model=PaygoRecords)
async def get_paygo_record_by_product_serial_number( # Original function name
    product_serial_number: str, # Original parameter name
    session: AsyncSession = Depends(get_session),
) -> PaygoRecords:
    """
    Retrieve a single Paygo record by its product serial number.
    """
    # FIX: Call the correct method, which is now get_paygo_by_product_serial_number
    paygo_record = await paygo_service.get_paygo_by_product_serial_number(product_serial_number, session)
    if not paygo_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paygo record with serial number '{product_serial_number}' not found" # Updated detail message
        )
    return paygo_record


@paygo_router.patch("/{paygo_uid}", response_model=PaygoRecords)
async def update_paygo_record(
    paygo_uid: UUID,
    paygo_update_data: PaygoUpdate,
    session: AsyncSession = Depends(get_session),
) -> PaygoRecords:
    """
    Update an existing Paygo record by its UID.
    Partial updates are supported.
    """
    updated_paygo_record = await paygo_service.update_paygo(paygo_uid, paygo_update_data, session)
    if not updated_paygo_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paygo record with UID '{paygo_uid}' not found"
        )
    return updated_paygo_record


@paygo_router.delete("/{paygo_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_paygo_record(
    paygo_uid: UUID,
    session: AsyncSession = Depends(get_session),
):
    """
    Delete a Paygo record by its UID.
    Returns 204 No Content on successful deletion.
    """
    was_deleted = await paygo_service.delete_paygo(paygo_uid, session)
    if not was_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paygo record with UID '{paygo_uid}' not found"
        )
    return None