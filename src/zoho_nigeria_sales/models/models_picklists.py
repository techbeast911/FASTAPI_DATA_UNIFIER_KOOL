from sqlalchemy import Column, String, DateTime
from sqlalchemy import Column, String, Boolean, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from src.zoho_nigeria_inventory.db.database import Base

class Picklist(Base):
    __tablename__ = "picklists"
    __table_args__ = {"schema": "zoho_nigeria_sales"}  # Same schema as your Customer model

    # Primary key and identification
    picklist_id = Column(String, primary_key=True, index=True)
    picklist_number = Column(String, index=True, unique=True)  # Often used as reference
    
    # Date information
    date = Column(DateTime)  # Picklist date
    created_time = Column(DateTime)  # System creation timestamp
    last_modified_time = Column(DateTime)  # Last update timestamp
    
    # Assignment details
    assignee_id = Column(String)  # ID of assigned staff
    assignee_name = Column(String)  # Name of assigned staff
    
    # Warehouse information
    warehouse_id = Column(String, index=True)  # Warehouse ID
    warehouse_name = Column(String)  # Warehouse name
    
    # Status tracking
    status = Column(String)  # Current status (e.g., "draft", "in_progress", "completed")
    
    # Additional information
    notes = Column(String)  # Optional notes/comments
    
    # Extended fields (similar to your Customer model)
    custom_fields = Column(JSONB)  # For any custom fields
    tags = Column(JSONB)  # For tagging/labeling picklists
    has_attachment = Column(Boolean, default=False)  # If documents are attached
    
    # Formatted versions if needed
    status_formatted = Column(String)  # Human-readable status
    date_formatted = Column(String)  # Formatted date string


    # # Optional relationship fields (add if needed)
    # salesorder_id = Column(String)  # Link to sales order
    # salesorder_number = Column(String)  # For easy reference

    # Add relationship to SalesOrder
    # salesorder_id = Column(String, ForeignKey('zoho_nigeria_sales.sales_orders.salesorder_id'))
    # sales_order = relationship("SalesOrder", back_populates="picklists")