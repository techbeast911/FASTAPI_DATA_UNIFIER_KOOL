from uuid import UUID
from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, desc

from src.kool_assembly.models.models_quality import Quality
from src.kool_assembly.schemas.schemas_quality import QualityCreate, QualityRecord, QualityUpdate

class QualityServices:
    """
    Service class for performing CRUD operations on Quality records.
    """

    async def get_all_quality(self, session: AsyncSession) -> List[QualityRecord]:
        """
        Retrieves all Quality records from the database, ordered by creation date descending.
        """
        statement = select(Quality).order_by(desc(Quality.created_at))
        result = await session.execute(statement)
        quality_records = result.scalars().all()
        return [QualityRecord.model_validate(quality, from_attributes=True) for quality in quality_records]

    async def get_quality_by_uid(self, uid: UUID, session: AsyncSession) -> Optional[QualityRecord]:
        """
        Retrieves a single Quality record by its unique UID.
        """
        quality = await session.get(Quality, uid)
        return QualityRecord.model_validate(quality, from_attributes=True) if quality else None

    async def get_quality_by_product_serial_number(self, product_serial_number: str, session: AsyncSession) -> Optional[QualityRecord]:
        """
        Retrieves a single Quality record by its product serial number.
        NOTE: This assumes your 'Quality' model has a 'product_serial_number' field.
              Adjust the field name if your model uses something else (e.g., 'batch_number', 'test_id').
        """
        statement = select(Quality).where(Quality.product_serial_number == product_serial_number) # Assuming 'product_serial_number' field
        result = await session.execute(statement)
        quality = result.scalars().first()
        return QualityRecord.model_validate(quality, from_attributes=True) if quality else None

    async def create_quality(self, quality_create: QualityCreate, session: AsyncSession) -> QualityRecord:
        """
        Creates a new Quality record in the database.
        """
        quality_data_dict = quality_create.model_dump()
        db_quality = Quality(**quality_data_dict)

        session.add(db_quality)
        await session.commit()
        await session.refresh(db_quality)

        return QualityRecord.model_validate(db_quality, from_attributes=True)

    async def update_quality(self, uid: UUID, quality_update: QualityUpdate, session: AsyncSession) -> Optional[QualityRecord]:
        """
        Updates an existing Quality record by its unique UID.
        """
        db_quality = await session.get(Quality, uid)

        if not db_quality:
            return None

        update_data = quality_update.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(db_quality, key, value)

        session.add(db_quality) # Good practice to explicitly add, though often not strictly necessary for objects loaded via session.get()
        await session.commit()
        await session.refresh(db_quality)

        return QualityRecord.model_validate(db_quality, from_attributes=True)

    async def delete_quality(self, uid: UUID, session: AsyncSession) -> bool:
        """
        Deletes a Quality record from the database by its UID.
        """
        quality_to_delete = await session.get(Quality, uid)
        if quality_to_delete:
            await session.delete(quality_to_delete)
            await session.commit()
            return True
        else:
            return False