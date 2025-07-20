from pydantic import BaseModel
from uuid import UUID,uuid4
from datetime import datetime
from typing import Optional

class PaygoCreate(BaseModel):
    product_sku : str
    air_conditioner : Optional[str]= None
    product_serial_number : str
    paygo_id_kb_no : str
    customer_name : str
    paygo_or_usb : str
    paygo_technician : str
    assembly_remarks : str
    date_sent_out : Optional[datetime] = None


class PaygoRecords(BaseModel):
    uid : UUID
    created_at: datetime
    product_sku : str
    air_conditioner : str
    product_serial_number : str
    paygo_id_kb_no : str
    customer_name : str
    paygo_or_usb : str
    paygo_technician : str
    assembly_remarks : str
    date_sent_out : datetime

class PaygoUpdate(BaseModel):
    product_sku : Optional[str] = None
    air_conditioner : Optional[str] = None
    product_serial_number : Optional[str]= None
    paygo_id_kb_no : Optional[str]= None
    customer_name : Optional[str]= None
    paygo_or_usb : Optional[str]= None
    paygo_technician : Optional[str]= None
    assembly_remarks : Optional[str]= None
    date_sent_out : Optional[datetime]= None