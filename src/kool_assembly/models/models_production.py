from sqlmodel import SQLModel, Field, Column
import sqlalchemy.dialects.postgresql as pg
import uuid
from datetime import datetime
from typing import Optional
class Production(SQLModel , table=True):
    __tablename__ = "production"
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
    comp_fixing : str
    engineer_that_installed_compressor : str
    comp_controller_connection : str
    piping : str
    brazing : str
    vacumming : str
    gas_charging : str
    batching : str
    leak_test : str
    customer_name : str
    packaging : str
    drying : str
    officer_that_passed_freezer : str
    issue : str
    product_category_new_ref:str
    product_type: str
    assembly_remarks : str
    date_sent_out  : datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))

    

    def __repr__(self) -> str:
        return f" Production {self.product_serial_number}"