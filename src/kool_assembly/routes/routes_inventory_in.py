# File: src/kool_assembly/routes/routes_inventory_in.py
# -*- coding: utf-8 -*-


from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from uuid import UUID

from src.db.main import get_session
from sqlalchemy.ext.asyncio import AsyncSession

from src.kool_assembly.schemas.schemas_inventory_in import InventoryInCreate, InventoryInRecord, InventoryInUpdate
from src.kool_assembly.services.services_inventory_in import InventoryInService
#from src.auth.auth_dependencies import AccessTokenBearer




inventory_in_router = APIRouter(
    tags=["Inventory In"] # Tags for API documentation (Swagger UI)
)

inventory_in_service = InventoryInService()




@inventory_in_router.get("/", response_model=List[InventoryInRecord])
async def get_all_inventory_in(session: AsyncSession = Depends(get_session), ) -> List[InventoryInRecord]:
    """
    Retrieve a list of all inventory_in records.
    """
    #print(user_details)
    inventory_ins = await inventory_in_service.get_all_inventory_in(session)
    return inventory_ins


@inventory_in_router.post("/", response_model=InventoryInRecord, status_code=status.HTTP_201_CREATED)
async def create_inventory_in(
    inventory_in_data: InventoryInCreate,
    session: AsyncSession = Depends(get_session),
) -> InventoryInRecord:
    """
    Create a new inventory_in record.
    """
    new_inventory_in = await inventory_in_service.create_inventory_in(inventory_in_data, session)
    return new_inventory_in


@inventory_in_router.get("/{inventory_in_uid}", response_model=InventoryInRecord)
async def get_inventory_in_by_uid(
    inventory_in_uid: UUID,
    session: AsyncSession = Depends(get_session),
) -> InventoryInRecord:
    """
    Retrieve a single inventory_in record by its unique identifier (UID).
    """
    inventory_in = await inventory_in_service.get_inventory_in_by_uid(inventory_in_uid, session)
    if not inventory_in:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory In record with UID '{inventory_in_uid}' not found"
        )
    return inventory_in

@inventory_in_router.get("/serial/{product_serial_number}", response_model=InventoryInRecord)
async def get_inventory_in_by_serial_number(
    product_serial_number: str,
    session: AsyncSession = Depends(get_session),
) -> InventoryInRecord:
    """
    Retrieve a single inventory_in record by its product serial number.
    """
    inventory_in = await inventory_in_service.get_inventory_in_by_serial_number(product_serial_number, session)
    if not inventory_in:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory In record with serial number '{product_serial_number}' not found"
        )
    return inventory_in


@inventory_in_router.patch("/{inventory_in_uid}", response_model=InventoryInRecord)
async def update_inventory_in(
    inventory_in_uid: UUID,
    inventory_in_update_data: InventoryInUpdate,
    session: AsyncSession = Depends(get_session),
) -> InventoryInRecord:
    """
    Update an existing inventory_in record by its UID.
    Partial updates are supported.
    """
    updated_inventory_in = await inventory_in_service.update_inventory_in(inventory_in_uid, inventory_in_update_data, session)
    if not updated_inventory_in:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory In record with UID '{inventory_in_uid}' not found"
        )
    return updated_inventory_in


@inventory_in_router.delete("/{inventory_in_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_inventory_in(
    inventory_in_uid: UUID,
    session: AsyncSession = Depends(get_session),
):
    """
    Delete an inventory_in record by its UID.
    Returns 204 No Content on successful deletion.
    """
    was_deleted = await inventory_in_service.delete_inventory_in(inventory_in_uid, session)
    if not was_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory In record with UID '{inventory_in_uid}' not found"
        )
    return None