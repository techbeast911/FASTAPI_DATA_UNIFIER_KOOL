import httpx
import json
import asyncio
import traceback
from dateutil.parser import parse
from sqlalchemy import select
from sqlalchemy import types as sqltypes
import re

from src.config import CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN, ORG_ID
from src.zoho_nigeria_inventory.db.database import async_session
from src.zoho_nigeria_purchases.models.models_purchase_orders import PurchaseOrders


async def get_access_token():
    url = "https://accounts.zoho.com/oauth/v2/token"
    params = {
        "refresh_token": REFRESH_TOKEN,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token"
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, params=params)
        response.raise_for_status()
        return response.json()["access_token"]


async def fetch_all_purchase_orders():
    token = await get_access_token()
    all_orders = []
    page = 1
    per_page = 200

    async with httpx.AsyncClient() as client:
        while True:
            url = "https://inventory.zoho.com/api/v1/purchaseorders"
            headers = {
                "Authorization": f"Zoho-oauthtoken {token}",
                "X-com-zoho-inventory-organizationid": ORG_ID
            }
            params = {
                "page": page,
                "per_page": per_page
            }

            try:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
                orders = data.get("purchaseorders", [])

                if not orders:
                    break

                all_orders.extend(orders)
                if len(orders) < per_page:
                    break

                page += 1
                await asyncio.sleep(0.5)
            except Exception as e:
                print(f"❌ Error fetching purchase orders: {e}")
                traceback.print_exc()
                break

    print(f"✅ Fetched {len(all_orders)} purchase orders from Zoho")
    return all_orders


async def insert_purchase_orders_to_db(orders_list):
    print("📥 Inserting purchase orders into database...")
    async with async_session() as db:
        try:
            processed_count = 0
            for order_data in orders_list:
                row_data = {}

                for key, value in order_data.items():
                    if not hasattr(PurchaseOrders, key):
                        continue

                    column = getattr(PurchaseOrders, key)
                    column_type = column.type

                    # Normalize blank strings
                    if isinstance(value, str) and value.strip() == "":
                        value = None

                    # Handle datetime fields
                    if isinstance(column_type, sqltypes.DateTime):
                        try:
                            if value:
                                dt = parse(value)
                                if dt.tzinfo:
                                    dt = dt.replace(tzinfo=None)
                                value = dt
                        except Exception:
                            print(f"⚠️ Could not parse datetime for {key}: {value}")
                            value = None

                    # Handle JSON fields
                    if isinstance(column_type, sqltypes.JSON):
                        if isinstance(value, str):
                            try:
                                value = json.loads(value)
                            except Exception:
                                value = {}
                        elif value is None:
                            value = {}

                    # Handle float fields
                    if isinstance(column_type, sqltypes.Float) and isinstance(value, str):
                        try:
                            value = float(value)
                        except ValueError:
                            value = None

                    # Handle integer fields that may come as descriptive strings
                    if isinstance(column_type, sqltypes.Integer):
                        if isinstance(value, str):
                            # Extract numbers from string (e.g., "Overdue by 34 days" → 34)
                            match = re.search(r'\d+', value)
                            value = int(match.group()) if match else None
                        elif not isinstance(value, int):
                            value = None

                    # Auto-cast to string if needed
                    if isinstance(column_type, (sqltypes.String, sqltypes.Text)):
                        if value is not None and not isinstance(value, str):
                            value = str(value)

                    row_data[key] = value

                order_id = row_data.get("purchaseorder_id")
                if not order_id:
                    continue

                result = await db.execute(select(PurchaseOrders).filter_by(purchaseorder_id=order_id))
                existing_order = result.scalars().first()

                if existing_order:
                    for attr, val in row_data.items():
                        if hasattr(existing_order, attr):
                            setattr(existing_order, attr, val)
                else:
                    order = PurchaseOrders(**row_data)
                    db.add(order)

                processed_count += 1

            await db.commit()
            print(f"✅ Successfully inserted/updated {processed_count} purchase orders.")
        except Exception as e:
            await db.rollback()
            print(f"❌ Error inserting purchase orders: {e}")
            traceback.print_exc()


async def sync_purchase_orders():
    print("🚀 Starting purchase order sync...")
    orders = await fetch_all_purchase_orders()
    if orders:
        await insert_purchase_orders_to_db(orders)
    else:
        print("ℹ️ No purchase orders found.")
    print("🏁 Purchase order sync completed.")
