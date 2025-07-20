from uuid import UUID
from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, desc

from src.kool_assembly.models.models_production import Production
from src.kool_assembly.schemas.schemas_production import ProductionCreate, ProductionRecord, ProductionUpdate

class ProductionService:
    """
    Service class for performing CRUD operations on Production records.
    """

    async def get_all_production(self, session: AsyncSession) -> List[ProductionRecord]:
        """
        Retrieves all Production records from the database, ordered by creation date descending.
        """
        statement = select(Production).order_by(desc(Production.created_at))
        result = await session.execute(statement)
        production_records = result.scalars().all()
        return [ProductionRecord.model_validate(production, from_attributes=True) for production in production_records]

    async def get_production_by_uid(self, uid: UUID, session: AsyncSession) -> Optional[ProductionRecord]:
        """
        Retrieves a single Production record by its unique UID.
        """
        production = await session.get(Production, uid)
        return ProductionRecord.model_validate(production, from_attributes=True) if production else None

    async def get_production_by_product_serial_number(self, product_serial_number: str, session: AsyncSession) -> Optional[ProductionRecord]:
        """
        Retrieves a single Production record by its product serial number.
        NOTE: This assumes your 'Production' model has a 'product_serial_number' field.
              Adjust the field name if your model uses something else (e.g., 'batch_number', 'product_sku').
        """
        statement = select(Production).where(Production.product_serial_number == product_serial_number) # Assuming 'product_serial_number' field
        result = await session.execute(statement)
        production = result.scalars().first()
        return ProductionRecord.model_validate(production, from_attributes=True) if production else None

    async def create_production(self, production_create: ProductionCreate, session: AsyncSession) -> ProductionRecord:
        """
        Creates a new Production record in the database.
        """
        production_data_dict = production_create.model_dump()
        db_production = Production(**production_data_dict)

        session.add(db_production)
        await session.commit()
        await session.refresh(db_production)

        return ProductionRecord.model_validate(db_production, from_attributes=True)

    async def update_production(self, uid: UUID, production_update: ProductionUpdate, session: AsyncSession) -> Optional[ProductionRecord]:
        """
        Updates an existing Production record by its unique UID.
        """
        db_production = await session.get(Production, uid)

        if not db_production:
            return None

        update_data = production_update.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(db_production, key, value)

        session.add(db_production) # Good practice to explicitly add, though often not strictly necessary for objects loaded via session.get()
        await session.commit()
        await session.refresh(db_production)

        return ProductionRecord.model_validate(db_production, from_attributes=True)

    async def delete_production(self, uid: UUID, session: AsyncSession) -> bool:
        """
        Deletes a Production record from the database by its UID.
        """
        production_to_delete = await session.get(Production, uid)
        if production_to_delete:
            await session.delete(production_to_delete)
            await session.commit()
            return True
        else:
            return False