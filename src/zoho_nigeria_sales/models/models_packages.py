from sqlalchemy import Column, String, Boolean, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from src.zoho_nigeria_inventory.db.database import Base

class Package(Base):
    __tablename__ = "packages"
    __table_args__ = {"schema": "zoho_nigeria_sales"}  # Same schema as SalesOrder

    # Primary key and identification
    package_id = Column(String, primary_key=True, index=True)
    package_number = Column(String, index=True, unique=True)
    
    # Relationships
    #salesorder_id = Column(String, ForeignKey('zoho_nigeria_sales.sales_orders.salesorder_id'))
    #sales_order = relationship("SalesOrder", back_populates="packages")
    
    shipment_id = Column(String, index=True)
    #customer_id = Column(String, ForeignKey('zoho_nigeria_sales.customers.contact_id'))
    #customer = relationship("Customer", back_populates="packages")
    
    # Package information
    customer_name = Column(String)
    status = Column(String)
    tracking_number = Column(String)
    is_tracking_enabled = Column(Boolean)
    shipment_type = Column(String)
    shipping_charge = Column(Float)
    quantity = Column(Float)
    
    # Date information
    date = Column(DateTime)
    created_time = Column(DateTime)
    last_modified_time = Column(DateTime)
    shipment_date = Column(DateTime)
    
    # Sales order reference
    salesorder_number = Column(String)
    sales_channel = Column(String)
    
    # Shipping details
    delivery_method = Column(String)
    is_carrier_shipment = Column(Boolean)
    label_format = Column(String)
    
    # Additional fields
    custom_fields = Column(JSONB)
    tags = Column(JSONB)