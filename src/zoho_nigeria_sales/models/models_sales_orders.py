from sqlalchemy import Column, String, Boolean, Float, DateTime, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from src.zoho_nigeria_inventory.db.database import Base

class SalesOrder(Base):
    __tablename__ = "sales_orders"
    __table_args__ = {"schema": "zoho_nigeria_sales"}

    # Primary key and basic fields
    salesorder_id = Column(String, primary_key=True, index=True)
    zcrm_potential_id = Column(String)
    zcrm_potential_name = Column(String)
    customer_name = Column(String)
    customer_id = Column(String, index=True)
    email = Column(String)
    delivery_date = Column(DateTime)
    company_name = Column(String)
    color_code = Column(String)
    
    # Status information
    current_sub_status_id = Column(String)
    current_sub_status = Column(String)
    pickup_location_id = Column(String)
    salesorder_number = Column(String, index=True)
    reference_number = Column(String)
    date = Column(DateTime)
    shipment_date = Column(DateTime)
    shipment_days = Column(Integer)
    due_by_days = Column(Integer)
    due_in_days = Column(Integer)
    
    # Financial information
    currency_id = Column(String)
    source = Column(String)
    currency_code = Column(String)
    total = Column(Float)
    bcy_total = Column(Float)
    total_invoiced_amount = Column(Float)
    balance = Column(Float)
    
    # Timestamps
    created_time = Column(DateTime)
    last_modified_time = Column(DateTime)
    
    # Email and notification flags
    is_emailed = Column(Boolean)
    is_viewed_in_mail = Column(Boolean)
    mail_first_viewed_time = Column(DateTime)
    mail_last_viewed_time = Column(DateTime)
    
    # Quantity information
    quantity = Column(Float)
    quantity_invoiced = Column(Float)
    quantity_packed = Column(Float)
    quantity_shipped = Column(Float)
    
    # Status flags
    order_status = Column(String)
    invoiced_status = Column(String)
    paid_status = Column(String)
    shipped_status = Column(String)
    status = Column(String)
    
    # Fulfillment information
    order_fulfillment_type = Column(String)
    is_drop_shipment = Column(Boolean)
    is_backorder = Column(Boolean)
    is_manually_fulfilled = Column(Boolean)
    is_scheduled_for_quick_shipment_create = Column(Boolean)
    
    # Sales channel
    sales_channel = Column(String)
    sales_channel_formatted = Column(String)
    salesperson_name = Column(String)
    
    # Location information
    branch_id = Column(String)
    branch_name = Column(String)
    location_id = Column(String)
    
    # Delivery information
    delivery_method = Column(String)
    delivery_method_id = Column(String)
    
    # Attachments and tags
    has_attachment = Column(Boolean)
    tags = Column(JSONB)
    
    # Custom fields
    cf_installment_in_months = Column(String)
    cf_installment_in_months_unformatted = Column(String)
    cf_business_units = Column(String)
    cf_business_units_unformatted = Column(String)
    cf_delivery_details = Column(String)
    cf_delivery_details_unformatted = Column(String)
    cf_acknowledge_application_for = Column(String)
    cf_acknowledge_application_for_unformatted = Column(String)
    cf_acknowledge_application_for_1 = Column(String)
    cf_acknowledge_application_for_1_unformatted = Column(String)
    cf_product_type = Column(String)
    cf_product_type_unformatted = Column(String)
    cf_actual_sales_order_date = Column(String)
    cf_actual_sales_order_date_unformatted = Column(String)
    cf_package_detail = Column(String)
    cf_package_detail_unformatted = Column(String)
    
    # JSON fields for complex data
    custom_fields = Column(JSONB)
    line_items = Column(JSONB)  # Consider adding if you need to store line items

     # Add foreign key reference to Customer
    #customer_id = Column(String, ForeignKey('zoho_nigeria_sales.customers.contact_id'))
    
    # Add relationship to Customer
    # customer = relationship(
    #     "Customer", 
    #     back_populates="sales_orders"
    # )

    # # Add relationship to Picklist
    # picklists = relationship("Picklist", back_populates="sales_order")

    # # Add relationship to Package
    # packages = relationship("Package", back_populates="sales_order")

    # invoices = relationship("Invoice", back_populates="sales_order")