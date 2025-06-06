# -*- coding: utf-8 -*-
import httpx
import json
import asyncio
import traceback
from datetime import datetime
from dateutil.parser import parse
from sqlalchemy import types as sqltypes
from sqlalchemy import select
from src.config import CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN, ORG_ID
from src.zoho_nigeria_inventory.db.database import async_session
from src.zoho_nigeria_sales.models.models_sales_orders import SalesOrder

async def get_access_token(max_retries=3, retry_delay=5):
    """Shared access token function with retry logic"""
    url = "https://accounts.zoho.com/oauth/v2/token"
    params = {
        "refresh_token": REFRESH_TOKEN,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for attempt in range(max_retries):
            try:
                response = await client.post(url, params=params)
                response.raise_for_status()
                return response.json()["access_token"]
            except httpx.ConnectTimeout:
                if attempt < max_retries - 1:
                    print(f"⌛ Connection timeout (attempt {attempt + 1}/{max_retries}), retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                    continue
                raise
            except httpx.HTTPStatusError as e:
                print(f"❌ HTTP error fetching access token: {e.response.status_code}")
                raise
            except Exception as e:
                print(f"❌ Unexpected error fetching access token: {str(e)}")
                raise

async def fetch_sales_orders(max_retries=3, retry_delay=5):
    """Fetch sales orders with improved error handling and retry logic"""
    print("🔍 Fetching sales orders from Zoho...")
    token = await get_access_token()
    page = 1
    per_page = 200
    all_sales_orders = []

    async with httpx.AsyncClient(timeout=30.0) as client:
        while True:
            url = "https://inventory.zoho.com/api/v1/salesorders"
            headers = {
                "Authorization": f"Zoho-oauthtoken {token}",
                "X-com-zoho-inventory-organizationid": ORG_ID
            }
            params = {
                "organization_id": ORG_ID,
                "page": page,
                "per_page": per_page,
                "include": "line_items"
            }

            for attempt in range(max_retries):
                try:
                    response = await client.get(url, headers=headers, params=params)
                    
                    if response.status_code != 200:
                        print(f"❌ Error fetching sales orders (Page {page}): {response.status_code}")
                        print(f"Response: {response.text[:200]}...")
                        
                        if response.status_code == 400:
                            error_data = response.json()
                            if error_data.get('code') == 2:  # Invalid parameter error
                                print("⚠️ Adjusting parameters and retrying...")
                                params = {
                                    "organization_id": ORG_ID,
                                    "page": page,
                                    "per_page": per_page
                                }
                                continue
                        response.raise_for_status()

                    data = response.json()
                    sales_orders = data.get("salesorders", [])
                    
                    if not sales_orders:
                        return all_sales_orders

                    all_sales_orders.extend(sales_orders)
                    
                    if len(sales_orders) < per_page:
                        return all_sales_orders
                        
                    page += 1
                    await asyncio.sleep(0.5)  # Rate limiting
                    break
                    
                except httpx.ConnectTimeout:
                    if attempt < max_retries - 1:
                        print(f"⌛ Connection timeout (attempt {attempt + 1}/{max_retries}), retrying in {retry_delay} seconds...")
                        await asyncio.sleep(retry_delay)
                        continue
                    raise
                except Exception as e:
                    print(f"❌ Error during sales order fetch (Page {page}): {str(e)}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_delay)
                        continue
                    raise

async def insert_sales_orders_to_db(sales_orders_from_api):
    """Insert or update sales orders with robust type handling"""
    print("📥 Inserting sales orders into database...")
    async with async_session() as db:
        try:
            processed_count = 0
            for order_payload in sales_orders_from_api:
                order_data = {}
                for key, value in order_payload.items():
                    if not hasattr(SalesOrder, key):
                        continue

                    column_attribute = getattr(SalesOrder, key)
                    model_column_type = column_attribute.type

                    # Handle empty strings
                    if isinstance(value, str) and value.strip() == "":
                        value = None
                    
                    if value is not None:
                        # Convert Python boolean to string if needed for string columns
                        if isinstance(value, bool) and isinstance(model_column_type, (sqltypes.String, sqltypes.Text, sqltypes.Unicode)):
                            value = str(value)
                        
                        # Handle numeric fields (Integer/Float)
                        elif isinstance(model_column_type, (sqltypes.Integer, sqltypes.Float)):
                            try:
                                if isinstance(value, str):
                                    # Enhanced number extraction from strings
                                    import re
                                    numbers = re.findall(r'-?\d+\.?\d*', value)  # Find all numbers including decimals
                                    if numbers:
                                        value = numbers[0]  # Take first found number
                                    else:
                                        value = 0
                                # Convert to appropriate numeric type
                                value = float(value) if isinstance(model_column_type, sqltypes.Float) else int(float(value))
                            except (ValueError, TypeError) as e:
                                print(f"⚠️ Could not convert to number for {key}: {value} - Using default 0")
                                value = 0  # Safe default for numeric fields
                        
                        # Handle date/datetime fields
                        elif key in ['date', 'delivery_date', 'shipment_date', 'created_time', 
                                   'last_modified_time', 'mail_first_viewed_time', 'mail_last_viewed_time']:
                            try:
                                if isinstance(value, str):
                                    dt = parse(value)
                                    if dt.tzinfo is not None:
                                        dt = dt.replace(tzinfo=None)
                                    value = dt
                            except (ValueError, TypeError):
                                print(f"⚠️ Could not parse datetime for {key}: {value}")
                                value = None
                        
                        # Handle JSON fields
                        elif key in ['custom_fields', 'tags', 'line_items', 'shipping_address', 
                                   'billing_address', 'documents']:
                            if isinstance(value, str):
                                try:
                                    value = json.loads(value)
                                except (json.JSONDecodeError, TypeError):
                                    print(f"⚠️ Could not parse JSON for {key}")
                                    value = {}
                            elif value is None:
                                value = {}

                    order_data[key] = value

                # Check if sales order exists
                order_id_val = order_data.get("salesorder_id")
                if not order_id_val:
                    print(f"⚠️ Skipping sales order with missing ID: {order_payload}")
                    continue

                result = await db.execute(
                    select(SalesOrder).filter_by(salesorder_id=order_id_val)
                )
                db_order = result.scalars().first()

                if db_order:
                    for attr_key, attr_value in order_data.items():
                        if hasattr(db_order, attr_key):
                            setattr(db_order, attr_key, attr_value)
                else:
                    db_order = SalesOrder(**order_data)
                    db.add(db_order)
                
                processed_count += 1

            await db.commit()
            print(f"✅ Successfully processed {processed_count} sales orders")
        except Exception as e:
            await db.rollback()
            print(f"❌ Error saving sales orders: {e}")
            traceback.print_exc()

async def sync_sales_orders(max_retries=3, retry_delay=5):
    """Complete sync workflow with proper error handling and retries"""
    print("🚀 Starting sales orders sync...")
    for attempt in range(max_retries):
        try:
            sales_orders = await fetch_sales_orders(max_retries, retry_delay)
            await insert_sales_orders_to_db(sales_orders)
            print("✅ Sales orders sync completed successfully")
            return
        except httpx.ConnectTimeout:
            if attempt < max_retries - 1:
                print(f"⌛ Connection timeout (attempt {attempt + 1}/{max_retries}), retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
                continue
            print("❌ Max retries reached for connection timeout")
            raise
        except Exception as e:
            print(f"❌ Sales orders sync failed: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
                continue
            traceback.print_exc()
            raise