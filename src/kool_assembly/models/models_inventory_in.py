from sqlmodel import SQLModel, Field, Column
import sqlalchemy.dialects.postgresql as pg
import uuid
from datetime import datetime
from typing import Optional


class Inventory_in(SQLModel , table=True):
    __tablename__ = "inventory_in"
    __table_args__ = {"schema": "kool_assembly"}

    uid: uuid.UUID = Field(
        default_factory=uuid.uuid4, 
        sa_column=Column(
            pg.UUID,
            primary_key=True,
            unique=True,
            nullable=False
        )
    )
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at: Optional[datetime] = Field(
        default_factory=datetime.now,
        sa_column=Column(pg.TIMESTAMP(timezone=True), onupdate=datetime.now, nullable=True) # nullable=True allows it to be null initially if DB schema allows
    )
    product_sku : str
    product_serial_number : str
    product_category_new_ref : str
    product_type : str
    brought_in_from : str
    # IMPORTANT: If date_logged_out is meant to be set only when it's "logged out",
    # then having a default=datetime.now might not be what you want.
    # If it can be null initially, make it Optional[datetime] and remove the default.
    # If it must always have a value upon creation, then default=datetime.now is fine.
    date_logged_out : datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))

    def __repr__(self) -> str:
        return f"Inventory_in {self.product_serial_number}"