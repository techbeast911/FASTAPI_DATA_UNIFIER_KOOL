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
from src.zoho_nigeria_sales.models.models_picklists import Picklist

async def get_access_token():
    """Reuse the same access token function from invoices"""
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

async def fetch_picklists():
    """Fetch picklists with improved error handling and logging"""
    print("🔍 Fetching picklists from Zoho...")
    token = await get_access_token()
    page = 1
    per_page = 200
    all_picklists = []

    async with httpx.AsyncClient(timeout=30.0) as client:
        while True:
            url = "https://inventory.zoho.com/api/v1/picklists"
            headers = {
                "Authorization": f"Zoho-oauthtoken {token}",
                "X-com-zoho-inventory-organizationid": ORG_ID
            }
            params = {
                "organization_id": ORG_ID,
                "page": page,
                "per_page": per_page,
                # Removed invalid sort parameters for picklists endpoint
                # According to Zoho API docs, picklists don't support sorting
            }

            try:
                response = await client.get(url, headers=headers, params=params)
                
                if response.status_code != 200:
                    print(f"❌ Error fetching picklists (Page {page}): {response.status_code}")
                    print(f"Response: {response.text[:200]}...")
                    
                    # Special handling for 400 errors
                    if response.status_code == 400:
                        error_data = response.json()
                        if error_data.get('code') == 2:  # Invalid parameter error
                            print("⚠️ Removing sort parameters and retrying...")
                            # Retry without sort parameters
                            params.pop('sort_column', None)
                            params.pop('sort_order', None)
                            response = await client.get(url, headers=headers, params=params)
                            if response.status_code == 200:
                                print("✅ Retry successful after removing sort parameters")
                            else:
                                response.raise_for_status()
                        else:
                            response.raise_for_status()
                    else:
                        response.raise_for_status()

                data = response.json()
                picklists = data.get("picklists", [])
                
                if not picklists:
                    break

                all_picklists.extend(picklists)
                
                if len(picklists) < per_page:
                    break
                    
                page += 1
                await asyncio.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                print(f"❌ Error during picklist fetch (Page {page}): {str(e)}")
                traceback.print_exc()
                break

    print(f"✅ Fetched {len(all_picklists)} picklists from Zoho")
    return all_picklists

async def insert_picklists_to_db(picklists_from_api):
    """Insert or update picklists with robust type handling"""
    print("📥 Inserting picklists into database...")
    async with async_session() as db:
        try:
            processed_count = 0
            for picklist_payload in picklists_from_api:
                pl_data = {}
                for key, value in picklist_payload.items():
                    if not hasattr(Picklist, key):
                        continue

                    column_attribute = getattr(Picklist, key)
                    model_column_type = column_attribute.type

                    # Handle empty strings
                    if isinstance(value, str) and value.strip() == "":
                        value = None
                    
                    if value is not None:
                        # Convert Python boolean to string if needed
                        if isinstance(value, bool) and isinstance(model_column_type, (sqltypes.String, sqltypes.Text, sqltypes.Unicode)):
                            value = str(value)
                        
                        # Handle date/datetime fields
                        elif key in ['date', 'created_time', 'last_modified_time']:
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
                        elif key in ['custom_fields', 'tags', 'items']:
                            if isinstance(value, str):
                                try:
                                    value = json.loads(value)
                                except (json.JSONDecodeError, TypeError):
                                    print(f"⚠️ Could not parse JSON for {key}")
                                    value = {}
                            elif value is None:
                                value = {}

                    pl_data[key] = value

                # Check if picklist exists
                picklist_id_val = pl_data.get("picklist_id")
                if not picklist_id_val:
                    print(f"⚠️ Skipping picklist with missing ID: {picklist_payload}")
                    continue

                result = await db.execute(
                    select(Picklist).filter_by(picklist_id=picklist_id_val)
                )
                db_picklist = result.scalars().first()

                if db_picklist:
                    for attr_key, attr_value in pl_data.items():
                        if hasattr(db_picklist, attr_key):
                            setattr(db_picklist, attr_key, attr_value)
                else:
                    db_picklist = Picklist(**pl_data)
                    db.add(db_picklist)
                
                processed_count += 1

            await db.commit()
            print(f"✅ Successfully processed {processed_count} picklists")
        except Exception as e:
            await db.rollback()
            print(f"❌ Error saving picklists: {e}")
            traceback.print_exc()

async def sync_picklists():
    """Complete sync workflow with proper error handling"""
    print("🚀 Starting picklists sync...")
    try:
        picklists = await fetch_picklists()
        await insert_picklists_to_db(picklists)
        print("✅ Picklists sync completed successfully")
    except Exception as e:
        print(f"❌ Picklists sync failed: {e}")
        traceback.print_exc()