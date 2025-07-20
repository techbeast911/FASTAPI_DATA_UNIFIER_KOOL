from sqlmodel import SQLModel, Field, Column
import sqlalchemy.dialects.postgresql as pg
import uuid
from datetime import datetime
from typing import Optional # Keep this import for Optional fields

class Inverters(SQLModel , table=True):
    __tablename__ = "inverters"
    __table_args__ = {"schema": "kool_assembly"}

    uid: uuid.UUID = Field(
        default_factory=uuid.uuid4, 
        sa_column=Column(
            pg.UUID(as_uuid=True),
            primary_key=True,
            unique=True,
            nullable=False
        )
    )
    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), default=datetime.now, nullable=False)
    )
    # **RECOMMENDED: Add updated_at field for better tracking**
    updated_at: Optional[datetime] = Field(
        default_factory=datetime.now,
        sa_column=Column(pg.TIMESTAMP(timezone=True), onupdate=datetime.now, nullable=True) # nullable=True allows it to be null initially if DB schema allows
    )

    engineer_name: str = Field(nullable=False) 
    inverter_size: str = Field(nullable=False) 
    customer_name: str = Field(nullable=False) 

    
    release_date: datetime = Field(sa_column=Column(pg.TIMESTAMP(timezone=True), default=datetime.now, nullable=False))

    return_inverter_id: Optional[str] = Field(default=None, nullable=True)
    return_date: Optional[datetime] = Field(default=None, sa_column=Column(pg.TIMESTAMP(timezone=True), nullable=True))


    def __repr__(self) -> str:
        return f"Inverters {self.engineer_name}"