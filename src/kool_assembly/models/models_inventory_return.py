from sqlmodel import SQLModel, Field, Column
import sqlalchemy.dialects.postgresql as pg
import uuid
from datetime import datetime
from typing import Optional

class Inventory_return(SQLModel , table=True):
    __tablename__ = "inventory returns"
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
    created_at : datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at: Optional[datetime] = Field(
        default_factory=datetime.now,
        sa_column=Column(pg.TIMESTAMP(timezone=True), onupdate=datetime.now, nullable=True) # nullable=True allows it to be null initially if DB schema allows
    )
    product_sku : str
    product_serial_number : str
    unit_received_by : str
    status : str
    released_to : str
    product_type : str
    date_sent_out : datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))


    def __repr__(self) -> str:
        return f"Inventory Return {self.product_serial_number}"