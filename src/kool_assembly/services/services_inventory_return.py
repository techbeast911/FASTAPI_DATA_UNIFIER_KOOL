from uuid import UUID
from typing import List, Optional
from datetime import datetime # Import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, desc

from src.kool_assembly.models.models_inventory_return import Inventory_return

from src.kool_assembly.schemas.schemas_inventory_return import InventoryReturnCreate, InventoryReturnRecord, InventoryReturnUpdate


class InventoryReturnService:
    """
    Service class for performing CRUD operations on Inventory_return records.
    """

    async def get_all_inventory_returns(self, session: AsyncSession) -> List[InventoryReturnRecord]:
        """
        Retrieves all inventory_return records from the database, ordered by creation date descending.
        """
        statement = select(Inventory_return).order_by(desc(Inventory_return.created_at))
        result = await session.execute(statement)
        inventory_returns = result.scalars().all()
        return [InventoryReturnRecord.model_validate(ir, from_attributes=True) for ir in inventory_returns]

    async def get_inventory_return_by_uid(self, uid: UUID, session: AsyncSession) -> Optional[InventoryReturnRecord]:
        """
        Retrieves a single inventory_return record by its unique UID.
        """
        inventory_return = await session.get(Inventory_return, uid)
        return InventoryReturnRecord.model_validate(inventory_return, from_attributes=True) if inventory_return else None

    async def get_inventory_return_by_product_serial_number(self, product_serial_number: str, session: AsyncSession) -> Optional[InventoryReturnRecord]:
        """
        Retrieves a single inventory_return record by its product serial number.
        """
        statement = select(Inventory_return).where(Inventory_return.product_serial_number == product_serial_number)
        result = await session.execute(statement)
        inventory_return = result.scalars().first()
        return InventoryReturnRecord.model_validate(inventory_return, from_attributes=True) if inventory_return else None


    async def create_inventory_return(self, inventory_return_create: InventoryReturnCreate, session: AsyncSession) -> InventoryReturnRecord:
        """
        Creates a new inventory_return record in the database.

        Args:
            inventory_return_create: The InventoryReturnCreate schema containing the data for the new inventory_return.
            session: The asynchronous database session.

        Returns:
            The newly created InventoryReturnRecord object.
        """
        inventory_return_data_dict = inventory_return_create.model_dump()

        db_inventory_return = Inventory_return(**inventory_return_data_dict)

        session.add(db_inventory_return)
        await session.commit()
        await session.refresh(db_inventory_return)

        return InventoryReturnRecord.model_validate(db_inventory_return, from_attributes=True)

    async def update_inventory_return(self, uid: UUID, inventory_return_update: InventoryReturnUpdate, session: AsyncSession) -> Optional[InventoryReturnRecord]:
        """
        Updates an existing inventory_return record in the database.
        """
        existing_inventory_return = await session.get(Inventory_return, uid)
        if not existing_inventory_return:
            return None

        update_data = inventory_return_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(existing_inventory_return, key, value)

        session.add(existing_inventory_return)
        await session.commit()
        await session.refresh(existing_inventory_return)

        return InventoryReturnRecord.model_validate(existing_inventory_return, from_attributes=True)

    async def delete_inventory_return(self, uid: UUID, session: AsyncSession) -> bool:
        """
        Deletes an inventory_return record from the database by its UID.
        """
        inventory_return_to_delete = await session.get(Inventory_return, uid)
        if inventory_return_to_delete:
            await session.delete(inventory_return_to_delete)
            await session.commit()
            return True
        else:
            return False