from uuid import UUID
from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, desc

from src.kool_assembly.models.models_iot import Iot
from src.kool_assembly.schemas.schemas_iot import IotCreate, IotRecord, IotUpdate

class IotService:
    """
    Service class for performing CRUD operations on IoT records.
    """

    async def get_all_iot(self, session: AsyncSession) -> List[IotRecord]:
        """
        Retrieves all IoT records from the database, ordered by creation date descending.
        """
        statement = select(Iot).order_by(desc(Iot.created_at))
        result = await session.execute(statement)
        iot_records = result.scalars().all()
        return [IotRecord.model_validate(iot, from_attributes=True) for iot in iot_records]

    async def get_iot_by_uid(self, uid: UUID, session: AsyncSession) -> Optional[IotRecord]:
        """
        Retrieves a single IoT record by its unique UID.
        """
        iot = await session.get(Iot, uid)
        return IotRecord.model_validate(iot, from_attributes=True) if iot else None

    async def get_iot_by_product_serial_number(self, product_serial_number: str, session: AsyncSession) -> Optional[IotRecord]:
        """
        Retrieves a single IoT record by its product serial number.
        """
        statement = select(Iot).where(Iot.product_serial_number == product_serial_number)
        result = await session.execute(statement)
        iot = result.scalars().first()
        return IotRecord.model_validate(iot, from_attributes=True) if iot else None


    async def create_iot(self, iot_create: IotCreate, session: AsyncSession) -> IotRecord:
        """
        Creates a new IoT record in the database.
        """
        iot_data_dict = iot_create.model_dump()
        db_iot = Iot(**iot_data_dict)

        session.add(db_iot)
        await session.commit()
        await session.refresh(db_iot)

        return IotRecord.model_validate(db_iot, from_attributes=True)

    async def update_iot(self, uid: UUID, iot_update: IotUpdate, session: AsyncSession) -> Optional[IotRecord]:
        """
        Updates an existing IoT record by its unique UID.
        """
        db_iot = await session.get(Iot, uid)

        if not db_iot:
            return None

        update_data = iot_update.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(db_iot, key, value)

        session.add(db_iot) # Explicitly add to session to track changes, good practice
        await session.commit()
        await session.refresh(db_iot)

        return IotRecord.model_validate(db_iot, from_attributes=True)

    async def delete_iot(self, uid: UUID, session: AsyncSession) -> bool:
        """
        Deletes an IoT record by its unique UID.
        """
        db_iot = await session.get(Iot, uid)

        if not db_iot:
            return False

        await session.delete(db_iot)
        await session.commit()

        return True