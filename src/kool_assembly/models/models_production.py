from sqlmodel import SQLModel, Field, Column
import sqlalchemy.dialects.postgresql as pg
import uuid
from datetime import datetime

class Production(SQLModel , table=True):
    __tablename__ = "production"
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