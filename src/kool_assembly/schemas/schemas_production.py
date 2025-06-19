from pydantic import BaseModel
from uuid import UUID,uuid4
from datetime import datetime
from typing import Optional

class ProductionCreate(BaseModel):

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
    date_sent_out  : Optional[datetime] = None

class ProductionRecord(BaseModel):
    uid: UUID
    created_at : datetime
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
    date_sent_out  : datetime



class ProductionUpdate(BaseModel):
    product_sku : Optional[str] = None
    product_serial_number : Optional[str] = None 
    comp_fixing : Optional[str] = None
    engineer_that_installed_compressor : Optional[str] =None
    comp_controller_connection : Optional[str] = None
    piping : Optional[str] = None
    brazing : Optional[str] = None
    vacumming : Optional[str] = None
    gas_charging : Optional[str] = None
    batching : Optional[str] = None
    leak_test : Optional[str] = None
    customer_name : Optional[str] = None
    packaging : Optional[str] = None
    drying : Optional[str] = None
    officer_that_passed_freezer : Optional[str] = None
    issue : Optional[str] = None
    product_category_new_ref:Optional[str] = None
    product_type: Optional[str] = None
    assembly_remarks : Optional[str] = None
    date_sent_out  : Optional[datetime] = None