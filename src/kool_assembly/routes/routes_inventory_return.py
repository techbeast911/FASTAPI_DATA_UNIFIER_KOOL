# File: src/kool_assembly/routes/routes_inventory_return.py
# -*- coding: utf-8 -*-

from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from uuid import UUID

from src.db.main import get_session   # Import the get_session function to obtain database sessions
from sqlalchemy.ext.asyncio import AsyncSession

from src.kool_assembly.schemas.schemas_inventory_return import InventoryReturnCreate, InventoryReturnRecord, InventoryReturnUpdate
from src.kool_assembly.services.services_inventory_return import InventoryReturnService


inventory_return_router = APIRouter(
    tags=["Inventory Return"]
)

inventory_return_service = InventoryReturnService()

@inventory_return_router.get("/", response_model=List[InventoryReturnRecord])
async def get_all_inventory_returns(session: AsyncSession = Depends(get_session)) -> List[InventoryReturnRecord]:
    """
    Retrieve a list of all inventory_return records.
    """
    inventory_returns = await inventory_return_service.get_all_inventory_returns(session)
    return inventory_returns

@inventory_return_router.post("/", response_model=InventoryReturnRecord, status_code=status.HTTP_201_CREATED)
async def create_inventory_return(
    inventory_return_data: InventoryReturnCreate,
    session: AsyncSession = Depends(get_session),
) -> InventoryReturnRecord:
    """
    Create a new inventory_return record.
    """
    new_inventory_return = await inventory_return_service.create_inventory_return(inventory_return_data, session)
    return new_inventory_return


@inventory_return_router.get("/{inventory_return_uid}", response_model=InventoryReturnRecord)
async def get_inventory_return_by_uid(
    inventory_return_uid: UUID,
    session: AsyncSession = Depends(get_session),
) -> InventoryReturnRecord:
    """
    Retrieve a single inventory_return record by its unique identifier (UID).
    """
    inventory_return = await inventory_return_service.get_inventory_return_by_uid(inventory_return_uid, session)
    if not inventory_return:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory Return record with UID '{inventory_return_uid}' not found"
        )
    return inventory_return

@inventory_return_router.get("/serial/{product_serial_number}", response_model=InventoryReturnRecord)
async def get_inventory_return_by_product_serial_number(
    product_serial_number: str,
    session: AsyncSession = Depends(get_session),
) -> InventoryReturnRecord:
    """
    Retrieve a single inventory_return record by its product serial number.
    """
    inventory_return = await inventory_return_service.get_inventory_return_by_product_serial_number(product_serial_number, session)
    if not inventory_return:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory Return record with serial number '{product_serial_number}' not found"
        )
    return inventory_return


@inventory_return_router.patch("/{inventory_return_uid}", response_model=InventoryReturnRecord)
async def update_inventory_return(
    inventory_return_uid: UUID,
    inventory_return_update_data: InventoryReturnUpdate,
    session: AsyncSession = Depends(get_session),
) -> InventoryReturnRecord:
    """
    Update an existing inventory_return record by its UID.
    Partial updates are supported.
    """
    updated_inventory_return = await inventory_return_service.update_inventory_return(inventory_return_uid, inventory_return_update_data, session)
    if not updated_inventory_return:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory Return record with UID '{inventory_return_uid}' not found"
        )
    return updated_inventory_return


@inventory_return_router.delete("/{inventory_return_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_inventory_return(
    inventory_return_uid: UUID,
    session: AsyncSession = Depends(get_session),
):
    """
    Delete an inventory_return record by its UID.
    Returns 204 No Content on successful deletion.
    """
    was_deleted = await inventory_return_service.delete_inventory_return(inventory_return_uid, session)
    if not was_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory Return record with UID '{inventory_return_uid}' not found"
        )
    return None