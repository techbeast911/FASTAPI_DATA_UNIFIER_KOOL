from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class InvertersCreate(BaseModel):
    # These fields are required when creating a new inverter
    engineer_name: str
    inverter_size: str
    customer_name: str
    # If release_date is ALWAYS set upon creation, remove Optional and default None
    # If it can genuinely be optional at creation, keep it, but ensure model also handles it.
    release_date: datetime # Assuming it's required for creation, or will default in model
    # If return_inverter_id is always provided on creation, keep as str
    # If it can be empty or null initially, make it Optional[str]
    return_inverter_id: Optional[str] = None # Assuming it might be null initially
    # return_date is almost certainly Optional for creation
    return_date: Optional[datetime] = None


class InvertersRecord(BaseModel):
    # This schema MUST accurately reflect what the Inverters SQLModel will contain
    uid: UUID
    created_at: datetime
    # Add updated_at if your model will have it
    updated_at: Optional[datetime] = None # Add this if your SQLModel has updated_at

    engineer_name: str
    inverter_size: str
    customer_name: str
   
    release_date: Optional[datetime] 
    return_inverter_id: Optional[str] 
    
    return_date: Optional[datetime] 

    # This is important for Pydantic to read from ORM attributes
    class Config:
        from_attributes = True # Pydantic V2 equivalent of orm_mode = True


class InvertersUpdate(BaseModel):
    
    engineer_name: Optional[str] = None
    inverter_size: Optional[str] = None
    customer_name: Optional[str] = None
    release_date: Optional[datetime] = None
    return_inverter_id: Optional[str] = None
    return_date: Optional[datetime] = None