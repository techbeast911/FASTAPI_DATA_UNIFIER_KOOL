from uuid import UUID
from typing import List, Optional
from datetime import datetime # Import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, desc

from src.kool_assembly.models.models_inventory_in import Inventory_in

from src.kool_assembly.schemas.schemas_inventory_in import InventoryInCreate, InventoryInRecord, InventoryInUpdate


class InventoryInService:
    # ... (other methods)

    async def create_inventory_in(self, inventory_in_create: InventoryInCreate, session: AsyncSession) -> InventoryInRecord:
        """
        Creates a new inventory_in record in the database.
        """
        inventory_in_data_dict = inventory_in_create.model_dump()

        db_inventory_in = Inventory_in(**inventory_in_data_dict)

        session.add(db_inventory_in)
        await session.commit()
        await session.refresh(db_inventory_in)

        # Convert the database object to the InventoryInRecord schema for the response.
        # FIX: Add from_attributes=True
        return InventoryInRecord.model_validate(db_inventory_in, from_attributes=True)

    
    async def update_inventory_in(self, uid: UUID, inventory_in_update: InventoryInUpdate, session: AsyncSession) -> Optional[InventoryInRecord]:
        """
        Updates an existing inventory_in record in the database.
        """
        # This line was missing or commented out, causing the NameError
        existing_inventory_in = await session.get(Inventory_in, uid)
        if not existing_inventory_in:
            return None

        update_data = inventory_in_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(existing_inventory_in, key, value)

        session.add(existing_inventory_in)
        await session.commit()
        await session.refresh(existing_inventory_in)
        return InventoryInRecord.model_validate(existing_inventory_in, from_attributes=True)

    # Make sure to also apply this fix in `get_all_inventory_in`, `get_inventory_in_by_uid`, and `get_inventory_in_by_serial_number`
    # wherever you are converting a `Battery` (or `Inventory_in`) object to `BatteryRecord` (or `InventoryInRecord`).

    async def get_all_inventory_in(self, session: AsyncSession) -> List[InventoryInRecord]:
        """
        Retrieves all inventory_in records from the database, ordered by creation date descending.
        """
        statement = select(Inventory_in).order_by(desc(Inventory_in.created_at))
        result = await session.execute(statement)
        inventory_ins = result.scalars().all()
        # FIX: Apply to all list comprehensions that convert ORM objects
        return [InventoryInRecord.model_validate(inventory_in, from_attributes=True) for inventory_in in inventory_ins]

    async def get_inventory_in_by_uid(self, uid: UUID, session: AsyncSession) -> Optional[InventoryInRecord]:
        """
        Retrieves a single inventory_in record by its unique UID.
        """
        inventory_in = await session.get(Inventory_in, uid)
        # FIX: Apply here
        return InventoryInRecord.model_validate(inventory_in, from_attributes=True) if inventory_in else None

    async def get_inventory_in_by_serial_number(self, product_serial_number: str, session: AsyncSession) -> Optional[InventoryInRecord]:
        """
        Retrieves a single inventory_in record by its product serial number.
        """
        statement = select(Inventory_in).where(Inventory_in.product_serial_number == product_serial_number)
        result = await session.execute(statement)
        inventory_in = result.scalars().first()
        # FIX: Apply here
        return InventoryInRecord.model_validate(inventory_in, from_attributes=True) if inventory_in else None

    async def delete_inventory_in(self, uid: UUID, session: AsyncSession) -> bool:
        """
        Deletes an inventory_in record from the database by its UID.
        """
        inventory_in_to_delete = await session.get(Inventory_in, uid)
        if inventory_in_to_delete:
            await session.delete(inventory_in_to_delete)
            await session.commit()
            return True
        else:
            return False