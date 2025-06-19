from uuid import UUID
from typing import List, Optional

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

        Args:
            session: The asynchronous database session.

        Returns:
            A list of BatteryRecord objects.
        """
        # Select all Battery records and order them by the 'created_at' field in descending order.
        # This will show the most recently created records first.
        statement = select(Battery).order_by(desc(Battery.created_at))
        result = await session.execute(statement)

        # Extract all scalar results (Battery objects)
        batteries = result.scalars().all()

        # Convert each Battery object to a BatteryRecord schema for consistent output.
        # This leverages Pydantic's ability to validate and serialize the ORM objects.
        return [BatteryRecord.model_validate(battery) for battery in batteries]

    async def get_battery_by_uid(self, uid: UUID, session: AsyncSession) -> Optional[BatteryRecord]:
        """
        Retrieves a single battery record by its unique UID.

        Args:
            uid: The UUID of the battery record to retrieve.
            session: The asynchronous database session.

        Returns:
            A BatteryRecord object if found, otherwise None.
        """
        # Use session.get() for efficient lookup by primary key (UID).
        battery = await session.get(Battery, uid)

        # If a battery is found, convert it to a BatteryRecord schema.
        # Otherwise, return None.
        return BatteryRecord.model_validate(battery) if battery else None

    async def get_battery_by_serial_number(self, product_serial_number: str, session: AsyncSession) -> Optional[BatteryRecord]:
        """
        Retrieves a single battery record by its product serial number.

        Args:
            product_serial_number: The serial number of the battery.
            session: The asynchronous database session.

        Returns:
            A BatteryRecord object if found, otherwise None.
        """
        # Build a select statement with a WHERE clause to filter by product_serial_number.
        statement = select(Battery).where(Battery.product_serial_number == product_serial_number)
        result = await session.execute(statement)

        # Get the first matching scalar result (Battery object).
        battery = result.scalars().first()

        # If a battery is found, convert it to a BatteryRecord schema.
        # Otherwise, return None.
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
        # Convert the Pydantic BatteryCreate object to a Battery SQLModel instance.
        # model_dump() converts the Pydantic model to a dictionary.
        # ** unpacks the dictionary into keyword arguments for the Battery constructor.
        db_battery = Battery.model_validate(battery_create.model_dump())

        # Add the new battery object to the session.
        session.add(db_battery)

        # Commit the transaction to save the new record to the database.
        await session.commit()

        # Refresh the object to load any database-generated values (like uid, created_at)
        # back into the db_battery object.
        await session.refresh(db_battery)

        # Convert the database object to the BatteryRecord schema for the response.
        return BatteryRecord.model_validate(db_battery)

    async def update_battery(self, uid: UUID, battery_update: BatteryUpdate, session: AsyncSession) -> Optional[BatteryRecord]:
        """
        Updates an existing battery record in the database.

        Args:
            uid: The UUID of the battery record to update.
            battery_update: The BatteryUpdate schema containing the fields to update.
            session: The asynchronous database session.

        Returns:
            The updated BatteryRecord object if found, otherwise None.
        """
        # First, retrieve the existing battery record.
        # It's better to get the direct SQLModel object here for setattr.
        existing_battery = await session.get(Battery, uid)

        # If the record is not found, return None.
        if not existing_battery:
            return None

        # Convert the BatteryUpdate schema to a dictionary,
        # excluding fields that were not set by the client (None values).
        update_data = battery_update.model_dump(exclude_unset=True)

        # Iterate over the provided update data and set the attributes on the existing object.
        for key, value in update_data.items():
            setattr(existing_battery, key, value)

        # Add the modified object back to the session (though it might already be tracked).
        session.add(existing_battery)

        # Commit the transaction to save the changes.
        await session.commit()

        # Refresh the object to reflect any database-side changes or triggers.
        await session.refresh(existing_battery)

        # Convert the updated database object to the BatteryRecord schema for the response.
        return BatteryRecord.model_validate(existing_battery)

    async def delete_battery(self, uid: UUID, session: AsyncSession) -> bool:
        """
        Deletes a battery record from the database by its UID.

        Args:
            uid: The UUID of the battery record to delete.
            session: The asynchronous database session.

        Returns:
            True if the record was deleted successfully, False otherwise.
        """
        # Retrieve the battery record to be deleted.
        # It's better to get the direct SQLModel object here for deletion.
        battery_to_delete = await session.get(Battery, uid)

        # If the record exists, delete it.
        if battery_to_delete:
            await session.delete(battery_to_delete)
            await session.commit() # Commit the deletion
            return True
        else:
            return False # Record not found