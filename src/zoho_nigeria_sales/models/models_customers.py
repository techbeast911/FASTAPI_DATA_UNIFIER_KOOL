from sqlalchemy import Column, String, Boolean, Float, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from src.zoho_nigeria_inventory.db.database import Base

class Customer(Base):
    __tablename__ = "customers"
    __table_args__ = {"schema": "zoho_nigeria_sales"}  

    contact_id = Column(String, primary_key=True, index=True)
    contact_name = Column(String)
    customer_name = Column(String)
    vendor_name = Column(String)
    contact_number = Column(String)
    company_name = Column(String)
    website = Column(String)
    language_code = Column(String)
    language_code_formatted = Column(String)
    contact_type = Column(String)
    contact_type_formatted = Column(String)
    status = Column(String)
    customer_sub_type = Column(String)
    source = Column(String)
    is_linked_with_zohocrm = Column(Boolean)
    payment_terms = Column(String)
    payment_terms_label = Column(String)
    currency_id = Column(String)
    twitter = Column(String)
    facebook = Column(String)
    currency_code = Column(String)
    outstanding_receivable_amount = Column(Float)
    outstanding_receivable_amount_bcy = Column(Float)
    outstanding_payable_amount = Column(Float)
    outstanding_payable_amount_bcy = Column(Float)
    unused_credits_receivable_amount = Column(Float)
    unused_credits_receivable_amount_bcy = Column(Float)
    unused_credits_payable_amount = Column(Float)
    unused_credits_payable_amount_bcy = Column(Float)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    phone = Column(String)
    mobile = Column(String)
    portal_status = Column(String)
    portal_status_formatted = Column(String)
    created_time = Column(DateTime)  # Could use DateTime
    created_time_formatted = Column(String)
    last_modified_time = Column(DateTime)  # Could use DateTime
    last_modified_time_formatted = Column(String)
    custom_fields = Column(JSONB)  # For storing complete custom fields
    custom_field_hash = Column(JSONB)  # Changed to JSONB based on previous error
    tags = Column(JSONB)  # Assuming tags might be an array
    ach_supported = Column(Boolean)
    has_attachment = Column(Boolean)
    non_default_currency_values = Column(JSONB)  # For complex currency data

    # # Add this relationship
    # sales_orders = relationship(
    #     "SalesOrder", 
    #     back_populates="customer",
    #     lazy="dynamic"  # Optional: controls how related items are loaded
    # )

    # # Add relationship to Package
    # packages = relationship("Package", back_populates="customer")

    #invoices = relationship("Invoice", back_populates="customer")