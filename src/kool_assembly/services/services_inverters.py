from uuid import UUID
from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, desc

from src.kool_assembly.models.models_inverters import Inverters
from src.kool_assembly.schemas.schemas_inverters import InvertersCreate, InvertersRecord, InvertersUpdate

class InvertersService:
    """
    Service class for performing CRUD operations on Inverters records.
    """

    async def get_all_inverters(self, session: AsyncSession) -> List[InvertersRecord]:
        """
        Retrieves all inverters records from the database, ordered by creation date descending.
        """
        statement = select(Inverters).order_by(desc(Inverters.created_at))
        result = await session.execute(statement)
        inverters = result.scalars().all()
        return [InvertersRecord.model_validate(inv, from_attributes=True) for inv in inverters]

    async def get_inverter_by_uid(self, uid: UUID, session: AsyncSession) -> Optional[InvertersRecord]:
        """
        Retrieves a single inverter record by its unique UID.
        """
        inverter = await session.get(Inverters, uid)
        return InvertersRecord.model_validate(inverter, from_attributes=True) if inverter else None

    async def get_inverter_by_product_serial_number(self, product_serial_number: str, session: AsyncSession) -> Optional[InvertersRecord]:
        """
        Retrieves a single inverter record by its product serial number.
        """
        statement = select(Inverters).where(Inverters.product_serial_number == product_serial_number)
        result = await session.execute(statement)
        inverter = result.scalars().first()
        return InvertersRecord.model_validate(inverter, from_attributes=True) if inverter else None

    async def create_inverter(self, inverter_create: InvertersCreate, session: AsyncSession) -> InvertersRecord:
        """
        Creates a new inverter record in the database.
        """
        inverter_data_dict = inverter_create.model_dump()
        db_inverter = Inverters(**inverter_data_dict)

        session.add(db_inverter)
        await session.commit()
        await session.refresh(db_inverter)

        
       
        return InvertersRecord.model_validate(db_inverter, from_attributes=True)

    async def update_inverter(self, uid: UUID, inverter_update: InvertersUpdate, session: AsyncSession) -> Optional[InvertersRecord]:
        """
        Updates an existing inverter record by its unique UID.
        """
        db_inverter = await session.get(Inverters, uid)

        if not db_inverter:
            return None

        update_data = inverter_update.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(db_inverter, key, value)

        session.add(db_inverter)
        await session.commit()
        await session.refresh(db_inverter)

        return InvertersRecord.model_validate(db_inverter, from_attributes=True)

    async def delete_inverter(self, uid: UUID, session: AsyncSession) -> bool:
        """
        Deletes an inverter record by its unique UID.
        """
        db_inverter = await session.get(Inverters, uid)

        if not db_inverter:
            return False

        await session.delete(db_inverter)
        await session.commit()

        return True