
from uuid import UUID
from typing import List, Optional
from datetime import datetime # Import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, desc

# Import your Battery model
from src.kool_assembly.models.models_battery import Battery

# Import your Pydantic schemas for Battery
from src.kool_assembly.schemas.schemas_batteries import BatteryCreate, BatteryRecord, BatteryUpdate


class BatteryService:
    """
    Service class for performing CRUD operations on Battery records.
    """

    async def get_all_batteries(self, session: AsyncSession) -> List[BatteryRecord]:
        """
        Retrieves all battery records from the database, ordered by creation date descending.
        """
        statement = select(Battery).order_by(desc(Battery.created_at))
        result = await session.execute(statement)
        batteries = result.scalars().all()
        return [BatteryRecord.model_validate(battery) for battery in batteries]

    async def get_battery_by_uid(self, uid: UUID, session: AsyncSession) -> Optional[BatteryRecord]:
        """
        Retrieves a single battery record by its unique UID.
        """
        battery = await session.get(Battery, uid)
        return BatteryRecord.model_validate(battery) if battery else None

    async def get_battery_by_serial_number(self, product_serial_number: str, session: AsyncSession) -> Optional[BatteryRecord]:
        """
        Retrieves a single battery record by its product serial number.
        """
        statement = select(Battery).where(Battery.product_serial_number == product_serial_number)
        result = await session.execute(statement)
        battery = result.scalars().first()
        return BatteryRecord.model_validate(battery) if battery else None


    async def create_battery(self, battery_create: BatteryCreate, session: AsyncSession) -> BatteryRecord:
        """
        Creates a new battery record in the database.

        Args:
            battery_create: The BatteryCreate schema containing the data for the new battery.
            session: The asynchronous database session.

        Returns:
            The newly created BatteryRecord object.
        """
        # Get data from the Pydantic schema as a dictionary
        battery_data_dict = battery_create.model_dump()

        # --- CRITICAL FIX FOR date_sent_out ---
        # If date_sent_out was not provided in the input (i.e., it's None),
        # explicitly set it to the current datetime before creating the SQLModel instance.
        # This ensures the SQLModel always receives a datetime for this non-nullable field
        # (even if it has a default_factory).
        if battery_data_dict.get("date_sent_out") is None:
            battery_data_dict["date_sent_out"] = datetime.now()

        # Instantiate the Battery SQLModel directly by unpacking the dictionary.
        # This correctly applies default_factory for uid and created_at.
        db_battery = Battery(**battery_data_dict)

        session.add(db_battery)
        await session.commit()
        await session.refresh(db_battery)

        # Convert the database object to the BatteryRecord schema for the response.
        # This will now succeed as db_battery.date_sent_out will always be a datetime.
        return BatteryRecord.model_validate(db_battery)


    async def update_battery(self, uid: UUID, battery_update: BatteryUpdate, session: AsyncSession) -> Optional[BatteryRecord]:
        """
        Updates an existing battery record in the database.
        """
        existing_battery = await session.get(Battery, uid)
        if not existing_battery:
            return None

        update_data = battery_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(existing_battery, key, value)

        session.add(existing_battery)
        await session.commit()
        await session.refresh(existing_battery)
        return BatteryRecord.model_validate(existing_battery)

    async def delete_battery(self, uid: UUID, session: AsyncSession) -> bool:
        """
        Deletes a battery record from the database by its UID.
        """
        battery_to_delete = await session.get(Battery, uid)
        if battery_to_delete:
            await session.delete(battery_to_delete)
            await session.commit()
            return True
        else:
            return False



