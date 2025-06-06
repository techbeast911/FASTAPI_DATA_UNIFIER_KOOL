import httpx
import json
import asyncio
import traceback
from datetime import datetime 
import json # Ensure json is imported
from dateutil.parser import parse
from sqlalchemy import types as sqltypes
from sqlalchemy import select
from src.config import CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN, ORG_ID
from src.zoho_nigeria_inventory.db.database import async_session
from src.zoho_nigeria_sales.models.models_invoices import Invoice

# -------------------------------------
# Get Zoho Access Token using Refresh Token
# -------------------------------------
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

# -------------------------------------
# Fetch All Invoices with Pagination
# -------------------------------------
async def fetch_invoices():
    token = await get_access_token()
    page = 1
    per_page = 200  # Zoho max
    all_invoices = []

    async with httpx.AsyncClient() as client:
        while True:
            url = "https://inventory.zoho.com/api/v1/invoices"
            headers = {
                "Authorization": f"Zoho-oauthtoken {token}",
                "X-com-zoho-inventory-organizationid": ORG_ID
            }
            params = {
                "page": page,
                "per_page": per_page
                # Optional: sort_column, sort_order can be added
            }

            response = await client.get(url, headers=headers, params=params)

            if response.status_code != 200:
                print("❌ Error fetching invoices from Zoho:")
                print(f"Status Code: {response.status_code}")
                print(f"Response: {response.text}")
                response.raise_for_status()

            data = response.json()
            invoices = data.get("invoices", [])

            if not invoices:
                break

            all_invoices.extend(invoices)

            if len(invoices) < per_page:
                break

            page += 1
            await asyncio.sleep(0.5)  # Respect Zoho rate limits

    print(f"✅ Fetched {len(all_invoices)} invoices from Zoho")
    return all_invoices

# -------------------------------------
# Insert or Update Invoices in PostgreSQL DB
# -------------------------------------
async def insert_invoices_to_db(invoices_from_api): # Renamed 'invoices' to avoid conflict
    print("📥 Inserting invoices into database...")
    async with async_session() as db:
        try:
            processed_count = 0
            for invoice_payload in invoices_from_api: # Iterating over data from Zoho API
                inv_data = {}
                for key, value in invoice_payload.items():
                    if not hasattr(Invoice, key): # Check if the key exists as an attribute in your Invoice model
                        continue

                    column_attribute = getattr(Invoice, key)
                    model_column_type = column_attribute.type # Get the SQLAlchemy type from your Invoice model

                    # 1. Handle empty strings: convert to None
                    if isinstance(value, str) and value.strip() == "":
                        value = None
                    
                    # 2. Main data type conversion logic
                    if value is not None: # Proceed with conversions only if value is not already None
                        # --- THIS IS THE KEY FIX ---
                        # Convert Python boolean to string if the Invoice model's column type is String-like
                        # (e.g., String, Text, Unicode, VARCHAR) and the incoming value is a boolean.
                        if isinstance(value, bool) and isinstance(model_column_type, (sqltypes.String, sqltypes.Text, sqltypes.Unicode)):
                            value = str(value)  # Converts True to "True", False to "False"
                        
                        # Handle date fields conversion (based on key name)
                        elif key in ['date', 'due_date']:
                            try:
                                # Ensure value is string-like before parsing, if not already a date object
                                value_str = str(value) if not isinstance(value, (str, datetime.date)) else value
                                if isinstance(value_str, str): # Only parse if it's a string
                                     value = datetime.strptime(value_str, '%Y-%m-%d').date()
                                # if it's already a date object from Zoho, it might be fine.
                            except (ValueError, TypeError):
                                print(f"⚠️ Warning: Could not parse date for key '{key}', value '{value}'. Setting to None.")
                                value = None
                        
                        # Handle datetime fields conversion (based on key name)
                        elif key in ['created_time', 'last_modified_time', 'updated_time', 
                                    'last_payment_date', 'client_viewed_time', 'payment_expected_date',
                                    'schedule_time', 'last_reminder_sent_date']:
                            try:
                                # Ensure value is string-like or datetime before parsing
                                value_str = str(value) if not isinstance(value, (str, datetime)) else value
                                if isinstance(value_str, str): # Only parse if it's a string
                                    dt = parse(value_str)
                                    if dt.tzinfo is not None:
                                        dt = dt.replace(tzinfo=None)  # Make timezone-naive
                                    value = dt
                                # if it's already a datetime object, it might be fine.
                            except (ValueError, TypeError):
                                print(f"⚠️ Warning: Could not parse datetime for key '{key}', value '{value}'. Setting to None.")
                                value = None
                        
                        # Handle JSON fields (based on key name)
                        # Your Invoice model defines these as JSONB, which can take Python dicts directly.
                        elif key in ['custom_fields', 'custom_field_hash', 'tags', 'documents',
                                    'billing_address', 'shipping_address']:
                            if isinstance(value, str): # If API gives a JSON string
                                try:
                                    value = json.loads(value)
                                except (json.JSONDecodeError, TypeError):
                                    print(f"⚠️ Warning: Could not parse JSON string for key '{key}', value '{value[:100]}...'. Setting to {{}}.")
                                    value = {}
                            elif value is None: # If empty string was converted to None, or API sent null
                                value = {} # Default to empty JSON object for JSONB
                            # If 'value' is already a dict/list from the API, it's suitable for JSONB.
                    
                    inv_data[key] = value

                # Check if invoice exists using invoice_id from inv_data
                invoice_id_val = inv_data.get("invoice_id")
                if not invoice_id_val:
                    print(f"⚠️ Warning: Skipping invoice due to missing 'invoice_id'. Data: {invoice_payload}")
                    continue

                result = await db.execute(
                    select(Invoice).filter_by(invoice_id=invoice_id_val)
                )
                db_invoice = result.scalars().first()

                if db_invoice: # Update existing invoice
                    for attr_key, attr_value in inv_data.items():
                        if hasattr(db_invoice, attr_key): # Ensure attribute exists before setting
                            setattr(db_invoice, attr_key, attr_value)
                else: # Create new invoice
                    db_invoice = Invoice(**inv_data)
                    db.add(db_invoice)
                processed_count +=1

            await db.commit()
            print(f"✅ Successfully processed and committed {processed_count} invoices.")
        except Exception as e:
            await db.rollback()
            print(f"❌ Error while inserting/updating invoices into database: {e}")
            traceback.print_exc()
# -------------------------------------
# Complete Sync Workflow Function
# (Use this for manual or scheduled sync)
# -------------------------------------
async def sync_invoices():
    try:
        invoices = await fetch_invoices()
        await insert_invoices_to_db(invoices)
    except Exception as e:
        print(f"❌ Error during invoices sync: {e}")
        traceback.print_exc()
