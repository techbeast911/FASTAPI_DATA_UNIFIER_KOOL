# import httpx
# import json
# import asyncio
# import traceback
# from datetime import datetime 
# from dateutil.parser import parse 
# from sqlalchemy import select
# from sqlalchemy import types as sqltypes 

# from src.config import CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN, ORG_ID 
# from src.zoho_nigeria_inventory.db.database import async_session
# from src.zoho_nigeria_purchases.models.models_vendors import Vendors 


# async def get_access_token():
#     url = "https://accounts.zoho.com/oauth/v2/token"
#     params = {
#         "refresh_token": REFRESH_TOKEN,
#         "client_id": CLIENT_ID,
#         "client_secret": CLIENT_SECRET,
#         "grant_type": "refresh_token"
#     }
#     async with httpx.AsyncClient() as client:
#         response = await client.post(url, params=params)
#         response.raise_for_status()
#         return response.json()["access_token"]


# async def fetch_all_vendors():
#     token = await get_access_token()
#     all_vendors = []
#     page = 1
#     per_page = 200

#     async with httpx.AsyncClient() as client:
#         while True:
#             url = "https://inventory.zoho.com/api/v1/contacts"
#             headers = {
#                 "Authorization": f"Zoho-oauthtoken {token}",
#                 "X-com-zoho-inventory-organizationid": ORG_ID
#             }
#             params = {
#                 "contact_type": "vendor",
#                 "page": page,
#                 "per_page": per_page
#             }

#             try:
#                 response = await client.get(url, headers=headers, params=params)
#                 response.raise_for_status()
#                 data = response.json()
#                 vendors = data.get("contacts", [])

#                 if not vendors:
#                     break

#                 all_vendors.extend(vendors)
#                 if len(vendors) < per_page:
#                     break

#                 page += 1
#                 await asyncio.sleep(0.5)  # rate limit
#             except Exception as e:
#                 print(f"❌ Error fetching vendors: {e}")
#                 traceback.print_exc()
#                 break

#     print(f"✅ Fetched {len(all_vendors)} vendors from Zoho")
#     return all_vendors


# async def insert_vendors_to_db(vendors_list):
#     print("📥 Inserting vendors into database...")
#     async with async_session() as db:
#         try:
#             processed_count = 0
#             for vendor_data in vendors_list:
#                 row_data = {}
#                 for key, value in vendor_data.items():
#                     if not hasattr(Vendors, key):
#                         continue

#                     column = getattr(Vendors, key)
#                     column_type = column.type

#                     # Normalize blank strings
#                     if isinstance(value, str) and value.strip() == "":
#                         value = None

#                     # Handle booleans stored as strings
#                     if isinstance(value, bool) and isinstance(column_type, (sqltypes.String, sqltypes.Text)):
#                         value = str(value)

#                     # Handle datetime parsing
#                     if key in ['created_time', 'last_modified_time']:
#                         try:
#                             if value:
#                                 dt = parse(value)
#                                 if dt.tzinfo:
#                                     dt = dt.replace(tzinfo=None)
#                                 value = dt
#                         except Exception:
#                             print(f"⚠️ Could not parse datetime for {key}: {value}")
#                             value = None

#                     # Handle JSON fields
#                     if key in ['custom_fields', 'tags', 'custom_field_hash', 'non_default_currency_values']:
#                         if isinstance(value, str):
#                             try:
#                                 value = json.loads(value)
#                             except Exception:
#                                 value = {}
#                         elif value is None:
#                             value = {}

#                     # Handle float fields
#                     if isinstance(column_type, sqltypes.Float) and isinstance(value, str):
#                         try:
#                             value = float(value)
#                         except ValueError:
#                             value = None

#                     row_data[key] = value

#                 contact_id = row_data.get("contact_id")
#                 if not contact_id:
#                     continue

#                 result = await db.execute(select(Vendors).filter_by(contact_id=contact_id))
#                 existing_vendor = result.scalars().first()

#                 if existing_vendor:
#                     for attr, val in row_data.items():
#                         if hasattr(existing_vendor, attr):
#                             setattr(existing_vendor, attr, val)
#                 else:
#                     vendor = Vendors(**row_data)
#                     db.add(vendor)

#                 processed_count += 1

#             await db.commit()
#             print(f"✅ Successfully inserted/updated {processed_count} vendors.")
#         except Exception as e:
#             await db.rollback()
#             print(f"❌ Error inserting vendors: {e}")
#             traceback.print_exc()


# async def sync_vendors():
#     print("🚀 Starting vendor sync...")
#     vendors = await fetch_all_vendors()
#     if vendors:
#         await insert_vendors_to_db(vendors)
#     else:
#         print("ℹ️ No vendors found.")
#     print("🏁 Vendor sync completed.")


import httpx
import json
import asyncio
import traceback
from datetime import datetime 
from dateutil.parser import parse 
from sqlalchemy import select
from sqlalchemy import types as sqltypes 

from src.config import CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN, ORG_ID 
from src.zoho_nigeria_inventory.db.database import async_session
from src.zoho_nigeria_purchases.models.models_vendors import Vendors 


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


async def fetch_all_vendors():
    token = await get_access_token()
    all_vendors = []
    page = 1
    per_page = 200

    async with httpx.AsyncClient() as client:
        while True:
            url = "https://inventory.zoho.com/api/v1/contacts"
            headers = {
                "Authorization": f"Zoho-oauthtoken {token}",
                "X-com-zoho-inventory-organizationid": ORG_ID
            }
            params = {
                "contact_type": "vendor",
                "page": page,
                "per_page": per_page
            }

            try:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
                vendors = data.get("contacts", [])

                if not vendors:
                    break

                all_vendors.extend(vendors)
                if len(vendors) < per_page:
                    break

                page += 1
                await asyncio.sleep(0.5)  # rate limit
            except Exception as e:
                print(f"❌ Error fetching vendors: {e}")
                traceback.print_exc()
                break

    print(f"✅ Fetched {len(all_vendors)} vendors from Zoho")
    return all_vendors


async def insert_vendors_to_db(vendors_list):
    print("📥 Inserting vendors into database...")
    async with async_session() as db:
        try:
            processed_count = 0
            for vendor_data in vendors_list:
                row_data = {}
                for key, value in vendor_data.items():
                    if not hasattr(Vendors, key):
                        continue

                    column = getattr(Vendors, key)
                    column_type = column.type

                    # Normalize blank strings
                    if isinstance(value, str) and value.strip() == "":
                        value = None

                    # Handle booleans stored as strings
                    if isinstance(value, bool) and isinstance(column_type, (sqltypes.String, sqltypes.Text)):
                        value = str(value)

                    # Handle datetime parsing
                    if key in ['created_time', 'last_modified_time']:
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
                    if key in ['custom_fields', 'tags', 'custom_field_hash', 'non_default_currency_values']:
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

                    # Auto-cast to string if column expects string
                    if isinstance(column_type, (sqltypes.String, sqltypes.Text)):
                        if value is not None and not isinstance(value, str):
                            value = str(value)

                    row_data[key] = value

                contact_id = row_data.get("contact_id")
                if not contact_id:
                    continue

                result = await db.execute(select(Vendors).filter_by(contact_id=contact_id))
                existing_vendor = result.scalars().first()

                if existing_vendor:
                    for attr, val in row_data.items():
                        if hasattr(existing_vendor, attr):
                            setattr(existing_vendor, attr, val)
                else:
                    vendor = Vendors(**row_data)
                    db.add(vendor)

                processed_count += 1

            await db.commit()
            print(f"✅ Successfully inserted/updated {processed_count} vendors.")
        except Exception as e:
            await db.rollback()
            print(f"❌ Error inserting vendors: {e}")
            traceback.print_exc()


async def sync_vendors():
    print("🚀 Starting vendor sync...")
    vendors = await fetch_all_vendors()
    if vendors:
        await insert_vendors_to_db(vendors)
    else:
        print("ℹ️ No vendors found.")
    print("🏁 Vendor sync completed.")
