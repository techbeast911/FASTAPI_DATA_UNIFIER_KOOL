# File: src/kool_assembly/routes/routes_production.py
# -*- coding: utf-8 -*-

from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from uuid import UUID

from src.db.main import get_session
from sqlalchemy.ext.asyncio import AsyncSession

from src.kool_assembly.schemas.schemas_production import ProductionCreate, ProductionRecord, ProductionUpdate
from src.kool_assembly.services.services_production import ProductionService

production_router = APIRouter(
    tags=["Production"]
)

production_service = ProductionService()

@production_router.get("/", response_model=List[ProductionRecord])
async def get_all_production_records(session: AsyncSession = Depends(get_session)) -> List[ProductionRecord]:
    """
    Retrieve a list of all Production records.
    """
    production_records = await production_service.get_all_production(session)
    return production_records

@production_router.post("/", response_model=ProductionRecord, status_code=status.HTTP_201_CREATED)
async def create_production_record(
    production_data: ProductionCreate,
    session: AsyncSession = Depends(get_session),
) -> ProductionRecord:
    """
    Create a new Production record.
    """
    new_production_record = await production_service.create_production(production_data, session)
    return new_production_record


@production_router.get("/{production_uid}", response_model=ProductionRecord)
async def get_production_record_by_uid(
    production_uid: UUID,
    session: AsyncSession = Depends(get_session),
) -> ProductionRecord:
    """
    Retrieve a single Production record by its unique identifier (UID).
    """
    production_record = await production_service.get_production_by_uid(production_uid, session)
    if not production_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Production record with UID '{production_uid}' not found"
        )
    return production_record

@production_router.get("/serial/{product_serial_number}", response_model=ProductionRecord)
async def get_production_record_by_product_serial_number(
    product_serial_number: str,
    session: AsyncSession = Depends(get_session),
) -> ProductionRecord:
    """
    Retrieve a single Production record by its product serial number.
    """
    production_record = await production_service.get_production_by_product_serial_number(product_serial_number, session)
    if not production_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Production record with serial number '{product_serial_number}' not found"
        )
    return production_record


@production_router.patch("/{production_uid}", response_model=ProductionRecord)
async def update_production_record(
    production_uid: UUID,
    production_update_data: ProductionUpdate,
    session: AsyncSession = Depends(get_session),
) -> ProductionRecord:
    """
    Update an existing Production record by its UID.
    Partial updates are supported.
    """
    updated_production_record = await production_service.update_production(production_uid, production_update_data, session)
    if not updated_production_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Production record with UID '{production_uid}' not found"
        )
    return updated_production_record


@production_router.delete("/{production_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_production_record(
    production_uid: UUID,
    session: AsyncSession = Depends(get_session),
):
    """
    Delete a Production record by its UID.
    Returns 204 No Content on successful deletion.
    """
    was_deleted = await production_service.delete_production(production_uid, session)
    if not was_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Production record with UID '{production_uid}' not found"
        )
    return None