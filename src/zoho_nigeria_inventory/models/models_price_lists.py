from sqlalchemy import Column, String, Boolean, Float
from sqlalchemy.dialects.postgresql import ARRAY
from src.zoho_nigeria_inventory.db.database import Base


class PriceList(Base):
    __tablename__ = "price_lists"
    __table_args__ = {"schema": "zoho_nigeria_inventory"}  # Same schema as CompositeItem

    pricebook_id = Column(String, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    currency_id = Column(String)
    currency_code = Column(String)
    status = Column(String)
    pricebook_type = Column(String)
    sales_or_purchase_type = Column(String)
    percentage = Column(Float)
    pricebook_rate = Column(Float)
    is_increase = Column(Boolean)
    rounding_type = Column(String)
    decimal_place = Column(Float)
    pricing_scheme = Column(String)
    last_modified_time = Column(String)  # Or DateTime if you prefer