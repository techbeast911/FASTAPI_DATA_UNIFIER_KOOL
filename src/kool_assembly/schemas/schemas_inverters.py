from pydantic import BaseModel
from uuid import UUID,uuid4
from datetime import datetime
from typing import Optional



class InvertersCreate(BaseModel):

    engineer_name : str
    inverter_size : str
    customer_name : str
    release_date : datetime = Optional[datetime] = None
    return_inverter_id : str
    return_date : datetime = Optional[datetime] = None


class InvertersRecord(BaseModel):

    uid : UUID
    created_at : datetime
    engineer_name : str
    inverter_size : str
    customer_name : str
    release_date : datetime
    return_inverter_id : str 
    return_date : datetime


class InvertersUpdate(BaseModel):
    engineer_name : Optional[str] = None
    inverter_size : Optional[str] = None
    customer_name : Optional[str] = None
    release_date : Optional[datetime] = None
    return_inverter_id : Optional[str] = None
    return_date : Optional[datetime] = None