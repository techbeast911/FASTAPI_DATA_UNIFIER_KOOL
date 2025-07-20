from sqlmodel import SQLModel, Field, Column
import sqlalchemy.dialects.postgresql as pg
import uuid
from datetime import datetime
from typing import Optional
class Quality(SQLModel , table=True):
    __tablename__ = "quality"
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
    product_serial_number: str
    product_sku: str
    product_category_new_ref: str
    performance: float
    accessories_checking : str
    product_type : str
    status : str
    officer_that_passed_freezer : str
    qc_remarks : str
    date_sent_out : datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))

    def __repr__(self) -> str:
        return f"Quality {self.product_serial_number}"