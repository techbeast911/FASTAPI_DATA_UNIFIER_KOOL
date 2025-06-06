from sqlalchemy import Column, String, Float, Boolean, DateTime, Integer
from sqlalchemy.dialects.postgresql import JSONB
from src.zoho_nigeria_inventory.db.database import Base

class PurchaseOrders(Base):
    __tablename__ = "purchase_orders"
    __table_args__ = {"schema": "zoho_nigeria_purchases"}

    purchaseorder_id = Column(String, primary_key=True, index=True)
    vendor_id = Column(String)
    vendor_name = Column(String)
    company_name = Column(String)
    order_status = Column(String)
    billed_status = Column(String)
    received_status = Column(String)
    status = Column(String)
    color_code = Column(String)
    current_sub_status_id = Column(String)
    current_sub_status = Column(String)
    purchaseorder_number = Column(String)
    reference_number = Column(String)
    date = Column(DateTime)
    delivery_date = Column(DateTime)
    expected_delivery_date = Column(DateTime)
    delivery_days = Column(Integer)
    due_by_days = Column(Integer)
    due_in_days = Column(Integer)
    currency_id = Column(String)
    currency_code = Column(String)
    price_precision = Column(Integer)
    total = Column(Float)
    has_attachment = Column(Boolean)
    tags = Column(JSONB)
    created_time = Column(DateTime)
    last_modified_time = Column(DateTime)
    is_drop_shipment = Column(Boolean)
    total_ordered_quantity = Column(Float)
    quantity_yet_to_receive = Column(Float)
    quantity_marked_as_received = Column(Float)
    is_po_marked_as_received = Column(Boolean)
    is_backorder = Column(Boolean)
    receives = Column(String)
    client_viewed_time = Column(DateTime)
    is_viewed_by_client = Column(Boolean)
    branch_id = Column(String)
    branch_name = Column(String)
    location_id = Column(String)


