from pydantic import BaseModel
from uuid import UUID,uuid4
from datetime import datetime
from typing import Optional

class InventoryReturnCreate(BaseModel):
    product_sku : str
    product_serial_number : str
    unit_received_by : str
    status : str
    released_to : str
    product_type : str
    date_sent_out : Optional[datetime] = None



class InventoryReturnRecord(BaseModel):

    uid: UUID
    created_at: datetime

    product_sku: str
    product_serial_number: str
    unit_received_by: str
    status: str
    released_to: str
    product_type: str
    date_sent_out: datetime



class InventoryReturnUpdate(BaseModel):

    product_sku : Optional[str] = None
    product_serial_number : Optional[str] = None
    unit_received_by : Optional[str] = None
    status : Optional[str] = None
    released_to : Optional[str] = None
    product_type : Optional[str] = None
    date_sent_out : Optional[datetime] = None

