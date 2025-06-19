from sqlmodel import SQLModel, Field, Column
import sqlalchemy.dialects.postgresql as pg
import uuid
from datetime import datetime


class Battery(SQLModel , table=True):
    __tablename__ = "battery"
    __table_args__ = {"schema": "kool_assembly"}

    uid:uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            primary_key=True,
            unique=True,
            nullable=False
        )
    )
    created_at : datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    customer_name : str
    product_sku : str
    product_serial_number : str
    field_technician : str
    condition : str
    receiver : str
    faulty_component : str
    remedy : str
    product_category_new_ref : str
    date_sent_out : datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))

    def __repr__(self) -> str:
        return f"Battery {self.field_technician}"