from pydantic import BaseModel
from uuid import UUID,uuid4
from datetime import datetime
from typing import Optional


class QualityCreate(BaseModel):
    product_serial_number: str
    product_sku: str
    product_category_new_ref: str
    performance: float
    accessories_checking : str
    product_type : str
    status : str
    officer_that_passed_freezer : str
    qc_remarks : str
    date_sent_out : Optional[datetime] = None


class QualityRecord(BaseModel):
    uid:UUID
    created_at:datetime
    product_serial_number: str
    product_sku: str
    product_category_new_ref: str
    performance: float
    accessories_checking : str
    product_type : str
    status : str
    officer_that_passed_freezer : str
    qc_remarks : str
    date_sent_out : datetime 

class QualityUpdate(BaseModel):

    product_serial_number: Optional[str] = None
    product_sku: Optional[str] = None
    product_category_new_ref: Optional[str] = None
    performance: Optional[float] = None
    accessories_checking : Optional[str] = None
    product_type : Optional[str] = None
    status : Optional[str] = None
    officer_that_passed_freezer : Optional[str] = None
    qc_remarks : Optional[str] = None
    date_sent_out : Optional[datetime] = None


