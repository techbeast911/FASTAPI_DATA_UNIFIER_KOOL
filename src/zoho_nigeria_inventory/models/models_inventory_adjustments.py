from sqlalchemy import Column, String, Boolean, Float, DateTime
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from src.zoho_nigeria_inventory.db.database import Base

class InventoryAdjustment(Base):
    __tablename__ = "inventory_adjustments"
    __table_args__ = {"schema": "zoho_nigeria_inventory"}

    inventory_adjustment_id = Column(String, primary_key=True, index=True)
    status = Column(String)
    adjustment_type = Column(String)
    date = Column(String)  # Could be DateTime if you prefer
    reason = Column(String)
    description = Column(String)
    total = Column(Float)
    created_time = Column(String)
    last_modified_time = Column(String)
    item_id = Column(String)
    name = Column(String)
    quantity_adjusted = Column(Float)
    value_adjusted = Column(Float)
    custom_fields = Column(JSONB)  # For storing the complete custom fields object
    custom_field_hash = Column(String)
    cf_spareparts_number = Column(String)
    cf_spareparts_number_unformatted = Column(String)
    cf_customer_name = Column(String)
    cf_customer_name_unformatted = Column(String)
    cf_contact_person = Column(String)
    cf_contact_person_unformatted = Column(String)
    cf_customer_address = Column(String)
    cf_customer_address_unformatted = Column(String)
    reference_number = Column(String)
    created_by_id = Column(String)
    created_by_name = Column(String)
    last_modified_by_id = Column(String)
    last_modified_by_name = Column(String)
    warehouse_id = Column(String)
    warehouse_name = Column(String)