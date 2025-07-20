from sqlmodel import SQLModel, Field, Column
import sqlalchemy.dialects.postgresql as pg
import uuid
from datetime import datetime
from typing import Optional

class Paygo(SQLModel , table=True):
    __tablename__ = "paygo"
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
    air_conditioner : str
    product_serial_number : str
    paygo_id_kb_no : str
    customer_name : str
    paygo_or_usb : str
    paygo_technician : str
    assembly_remarks : str
    date_sent_out : datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))

    def __repr__(self) -> str:
        return f"Paygo {self.paygo_id_kb_no}"