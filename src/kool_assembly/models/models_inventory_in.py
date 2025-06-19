from sqlmodel import SQLModel, Field, Column
import sqlalchemy.dialects.postgresql as pg
import uuid
from datetime import datetime


class Inventory_in(SQLModel , table=True):
    __tablename__ = "inventory_in"
    __table_args__ = {"schema": "kool_assembly"}

    uid:uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            primary_key=True,
            unique=True,
            nullable=False
        )
    )
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    product_sku : str
    product_serial_number : str
    product_category_new_ref : str
    product_type : str
    brought_in_from : str
    date_logged_out : datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))

    def __repr__(self) -> str:
        return f"Inventory_in {self.product_serial_number}"


