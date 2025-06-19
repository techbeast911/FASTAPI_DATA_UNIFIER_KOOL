from sqlmodel import SQLModel, Field, Column
import sqlalchemy.dialects.postgresql as pg
import uuid
from datetime import datetime

class Inverters(SQLModel , table=True):
    __tablename__ = "inverters"
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
    engineer_name : str
    inverter_size : str
    customer_name : str
    release_date : datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    return_inverter_id : str
    return_date : datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))

    def __repr__(self) -> str:
        return f"Inverters {self.engineer_name}"