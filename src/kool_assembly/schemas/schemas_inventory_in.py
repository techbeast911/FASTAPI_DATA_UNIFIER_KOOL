from pydantic import BaseModel
from uuid import UUID,uuid4
from datetime import datetime
from typing import Optional


class InventoryInCreate(BaseModel):
    product_sku : str
    product_serial_number : str
    product_category_new_ref : str
    product_type : str
    brought_in_from : str
    date_logged_out : Optional[datetime] = None 


class InventoryInRecord(BaseModel):

    uid: UUID 
    created_at: datetime 

    product_sku : str
    product_serial_number : str
    product_category_new_ref : str
    product_type : str
    brought_in_from : str
    date_logged_out : datetime 



class InventoryInUpdate(BaseModel):

    product_sku : Optional[str] = None
    product_serial_number : Optional[str] = None
    product_category_new_ref : Optional[str] = None
    product_type : Optional[str] = None
    brought_in_from : Optional[str] = None
    date_logged_out : Optional[datetime] = None

