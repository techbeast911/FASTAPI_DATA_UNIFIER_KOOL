
from uuid import UUID
from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, desc

from src.kool_assembly.models.models_paygo import Paygo
from src.kool_assembly.schemas.schemas_paygo import PaygoCreate, PaygoRecords, PaygoUpdate


class PaygoService:
    """
    Service class for performing CRUD operations on Paygo records.
    """

    async def get_all_paygo(self, session: AsyncSession) -> List[PaygoRecords]:
        """
        Retrieves all Paygo records from the database, ordered by creation date descending.
        """
        statement = select(Paygo).order_by(desc(Paygo.created_at))
        result = await session.execute(statement)
        paygo_records = result.scalars().all()
        return [PaygoRecords.model_validate(paygo, from_attributes=True) for paygo in paygo_records]

    async def get_paygo_by_uid(self, uid: UUID, session: AsyncSession) -> Optional[PaygoRecords]:
        """
        Retrieves a single Paygo record by its unique UID.
        """
        paygo = await session.get(Paygo, uid)
        return PaygoRecords.model_validate(paygo, from_attributes=True) if paygo else None

    
    async def get_paygo_by_product_serial_number(self, product_serial_number: str, session: AsyncSession) -> Optional[PaygoRecords]:
        """
        Retrieves a single Paygo record by its product serial number.
        """
        statement = select(Paygo).where(Paygo.product_serial_number == product_serial_number)
        result = await session.execute(statement)
        paygo = result.scalars().first()
        return PaygoRecords.model_validate(paygo, from_attributes=True) if paygo else None

    async def create_paygo(self, paygo_create: PaygoCreate, session: AsyncSession) -> PaygoRecords:
        """
        Creates a new Paygo record in the database.
        """
        paygo_data_dict = paygo_create.model_dump()
        db_paygo = Paygo(**paygo_data_dict)

        session.add(db_paygo)
        await session.commit()
        await session.refresh(db_paygo)

        return PaygoRecords.model_validate(db_paygo, from_attributes=True)

    async def update_paygo(self, uid: UUID, paygo_update: PaygoUpdate, session: AsyncSession) -> Optional[PaygoRecords]:
        """
        Updates an existing Paygo record by its unique UID.
        """
        db_paygo = await session.get(Paygo, uid)

        if not db_paygo:
            return None

        update_data = paygo_update.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(db_paygo, key, value)

        session.add(db_paygo)
        await session.commit()
        await session.refresh(db_paygo)

        return PaygoRecords.model_validate(db_paygo, from_attributes=True)

    async def delete_paygo(self, uid: UUID, session: AsyncSession) -> bool:
        """
        Deletes a Paygo record from the database by its UID.
        """
        paygo_to_delete = await session.get(Paygo, uid)
        if paygo_to_delete:
            await session.delete(paygo_to_delete)
            await session.commit()
            return True
        else:
            return False