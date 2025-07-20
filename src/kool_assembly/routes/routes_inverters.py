# File: src/kool_assembly/routes/routes_inverters.py
# -*- coding: utf-8 -*-

from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from uuid import UUID

from src.db.main import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from src.kool_assembly.schemas.schemas_inverters import InvertersCreate, InvertersRecord, InvertersUpdate
from src.kool_assembly.services.services_inverters import InvertersService

inverters_router = APIRouter(
    tags=["Inverters"]
)

inverters_service = InvertersService()

@inverters_router.get("/", response_model=List[InvertersRecord])
async def get_all_inverters(session: AsyncSession = Depends(get_session)) -> List[InvertersRecord]:
    """
    Retrieve a list of all inverters records.
    """
    inverters = await inverters_service.get_all_inverters(session)
    return inverters

@inverters_router.post("/", response_model=InvertersRecord, status_code=status.HTTP_201_CREATED)
async def create_inverter(
    inverter_data: InvertersCreate,
    session: AsyncSession = Depends(get_session),
) -> InvertersRecord:
    """
    Create a new inverter record.
    """
    new_inverter = await inverters_service.create_inverter(inverter_data, session)
    return new_inverter


@inverters_router.get("/{inverter_uid}", response_model=InvertersRecord)
async def get_inverter_by_uid(
    inverter_uid: UUID,
    session: AsyncSession = Depends(get_session),
) -> InvertersRecord:
    """
    Retrieve a single inverter record by its unique identifier (UID).
    """
    inverter = await inverters_service.get_inverter_by_uid(inverter_uid, session)
    if not inverter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inverter record with UID '{inverter_uid}' not found"
        )
    return inverter

# @inverters_router.get("/serial/{product_serial_number}", response_model=InvertersRecord)
# async def get_inverter_by_product_serial_number(
#     product_serial_number: str,
#     session: AsyncSession = Depends(get_session),
# ) -> InvertersRecord:
#     """
#     Retrieve a single inverter record by its product serial number.
#     """
#     inverter = await inverters_service.get_inverter_by_product_serial_number(product_serial_number, session)
#     if not inverter:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Inverter record with serial number '{product_serial_number}' not found"
#         )
#     return inverter


@inverters_router.patch("/{inverter_uid}", response_model=InvertersRecord)
async def update_inverter(
    inverter_uid: UUID,
    inverter_update_data: InvertersUpdate,
    session: AsyncSession = Depends(get_session),
) -> InvertersRecord:
    """
    Update an existing inverter record by its UID.
    Partial updates are supported.
    """
    updated_inverter = await inverters_service.update_inverter(inverter_uid, inverter_update_data, session)
    if not updated_inverter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inverter record with UID '{inverter_uid}' not found"
        )
    return updated_inverter


@inverters_router.delete("/{inverter_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_inverter(
    inverter_uid: UUID,
    session: AsyncSession = Depends(get_session),
):
    """
    Delete an inverter record by its UID.
    Returns 204 No Content on successful deletion.
    """
    was_deleted = await inverters_service.delete_inverter(inverter_uid, session)
    if not was_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inverter record with UID '{inverter_uid}' not found"
        )
    return None