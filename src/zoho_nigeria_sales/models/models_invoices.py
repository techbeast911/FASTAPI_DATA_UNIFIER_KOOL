from sqlalchemy import Column, String, Boolean, Float, Date, ForeignKey, Integer,DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from src.zoho_nigeria_inventory.db.database import Base

class Invoice(Base):
    __tablename__ = "invoices"
    __table_args__ = {"schema": "zoho_nigeria_sales"}

    # Primary key and identification
    invoice_id = Column(String, primary_key=True, index=True)
    invoice_number = Column(String, index=True, unique=True)
    
    # # Relationships
    # customer_id = Column(String, ForeignKey('zoho_nigeria_sales.customers.contact_id'))
    # customer = relationship("Customer", back_populates="invoices")
    
    # salesorder_id = Column(String, ForeignKey('zoho_nigeria_sales.sales_orders.salesorder_id'))
    # sales_order = relationship("SalesOrder", back_populates="invoices")
    
    zcrm_potential_id = Column(String)
    location_id = Column(String)
    branch_id = Column(String)
    
    # Customer information
    zcrm_potential_name = Column(String)
    customer_name = Column(String)
    company_name = Column(String)
    email = Column(String)
    phone = Column(String)
    salesperson_name = Column(String)
    salesperson_id = Column(String)
    
    # Address information
    billing_address = Column(JSONB)
    shipping_address = Column(JSONB)
    country = Column(String)
    
    # Financial information
    total = Column(Float)
    balance = Column(Float)
    shipping_charge = Column(Float)
    adjustment = Column(Float)
    write_off_amount = Column(Float)
    exchange_rate = Column(Float)
    unprocessed_payment_amount = Column(Float)
    
    # Status and dates
    status = Column(String)
    date = Column(Date)
    due_date = Column(Date)
    due_days = Column(Integer)
    payment_expected_date = Column(DateTime)
    created_time = Column(DateTime)
    last_modified_time = Column(DateTime)
    updated_time = Column(DateTime)
    last_payment_date = Column(DateTime)
    
    # Flags and indicators
    ach_payment_initiated = Column(Boolean)
    is_viewed_by_client = Column(Boolean)
    has_attachment = Column(Boolean)
    client_viewed_time = Column(DateTime)
    is_emailed = Column(Boolean)
    color_code = Column(String)
    
    # Currency information
    currency_id = Column(String)
    currency_code = Column(String)
    currency_symbol = Column(String)
    
    # Document details
    template_type = Column(String)
    no_of_copies = Column(Integer)
    show_no_of_copies = Column(Boolean)
    template_id = Column(String)
    documents = Column(JSONB)
    
    # Additional fields
    reference_number = Column(String)
    branch_name = Column(String)
    created_by = Column(String)
    current_sub_status_id = Column(String)
    current_sub_status = Column(String)
    schedule_time = Column(DateTime)
    transaction_type = Column(String)
    reminders_sent = Column(Integer)
    last_reminder_sent_date = Column(DateTime)
    
    # Custom fields
    custom_fields = Column(JSONB)
    custom_field_hash = Column(JSONB)
    cf_warrant_claim_request = Column(String)
    cf_warrant_claim_request_unformatted = Column(String)
    cf_installment_in_months = Column(String)
    cf_installment_in_months_unformatted = Column(String)
    cf_delivery_details = Column(String)
    cf_delivery_details_unformatted = Column(String)
    cf_acknowledge_application_for = Column(String)
    cf_acknowledge_application_for_unformatted = Column(String)
    cf_acknowledge_application_for_1 = Column(String)
    cf_acknowledge_application_for_1_unformatted = Column(String)
    cf_business_units = Column(String)
    cf_business_units_unformatted = Column(String)
    tags = Column(JSONB)