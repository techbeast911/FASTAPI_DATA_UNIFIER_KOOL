from pydantic import BaseModel
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional


class IotCreate(BaseModel):
    product_sku : str
    product_serial_number : str
    device_name : str
    unit_id : str
    customer_name : str
    product_category_new_ref : str
    engineer_name : str
    product_type : str
    # FIX: Use square brackets for Optional
    date_sent_out : Optional[datetime] = None


class IotRecord(BaseModel):
    uid : UUID
    created_at : datetime
    product_sku : str
    product_serial_number : str
    device_name : str
    unit_id : str
    customer_name : str
    product_category_new_ref : str
    engineer_name : str
    product_type : str
    # FIX: If this is a datetime, it should be datetime, not str
    date_sent_out : Optional[datetime] # Make it Optional here too if it can be null from the DB


class IotUpdate(BaseModel):
    product_sku : Optional[str] = None
    product_serial_number : Optional[str] = None
    device_name : Optional[str] = None
    unit_id : Optional[str] = None
    customer_name : Optional[str] = None
    product_category_new_ref : Optional[str] = None
    engineer_name : Optional[str] = None
    product_type : Optional[str] = None
    # FIX: If this is a datetime, it should be datetime, not str
    date_sent_out : Optional[datetime] = None