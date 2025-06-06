
import httpx
import json
import asyncio
import traceback
from datetime import datetime # Added
from dateutil.parser import parse # Added
from sqlalchemy import select
from sqlalchemy import types as sqltypes # Added

from src.config import CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN, ORG_ID # Ensure these are correctly sourced
from src.zoho_nigeria_inventory.db.database import async_session
from src.zoho_nigeria_sales.models.models_packages import Package # Your Package model


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

async def fetch_packages():
    token = await get_access_token()
    page = 1
    per_page = 200  # Zoho's max per page
    all_packages = []

    async with httpx.AsyncClient() as client:
        while True:
            url = "https://inventory.zoho.com/api/v1/packages"  # Zoho's package endpoint
            headers = {
                "Authorization": f"Zoho-oauthtoken {token}",
                "X-com-zoho-inventory-organizationid": ORG_ID
            }
            params = {
                # "organization_id": ORG_ID, # Usually not needed if X-com-zoho-inventory-organizationid is in header
                "page": page,
                "per_page": per_page,
                "sort_column": "last_modified_time",
                "sort_order": "D"  # Zoho API often uses "A" for Ascending, "D" for Descending
            }

            try:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status() # Will raise an HTTPError for bad responses (4XX or 5XX)
                data = response.json()
                packages_page = data.get("packages", [])

                if not packages_page:
                    break

                all_packages.extend(packages_page)
                
                if len(packages_page) < per_page: # Correct pagination check
                    break
                    
                page += 1
                await asyncio.sleep(0.5)  # Rate limiting
            except httpx.HTTPStatusError as e:
                print(f"❌ Error fetching packages from Zoho: {e.response.status_code} - {e.response.text}")
                break # Stop fetching on error
            except httpx.RequestError as e:
                print(f"❌ Request error while fetching packages: {e}")
                break # Stop fetching on error
            except json.JSONDecodeError as e:
                print(f"❌ Error decoding JSON response from Zoho packages API: {e}")
                break


    print(f"✅ Fetched {len(all_packages)} packages from Zoho")
    return all_packages

async def insert_packages_to_db(packages_from_api):
    print("📥 Inserting packages into database...")
    async with async_session() as db:
        try:
            processed_count = 0
            for package_payload in packages_from_api:
                pkg_data = {}
                for key, value in package_payload.items():
                    if not hasattr(Package, key):
                        continue

                    column_attribute = getattr(Package, key)
                    model_column_type = column_attribute.type

                    # 1. Handle general empty strings: convert to None
                    if isinstance(value, str) and value.strip() == "":
                        value = None
                    
                    # 2. Main data type conversion logic
                    if value is not None:
                        # Convert Python boolean to string if the Package model's column is String-like
                        if isinstance(value, bool) and isinstance(model_column_type, (sqltypes.String, sqltypes.Text, sqltypes.Unicode)):
                            value = str(value)
                        
                        # Handle DateTime fields (Package model uses DateTime for all date-like fields)
                        elif key in ['date', 'created_time', 'last_modified_time', 'shipment_date']:
                            try:
                                value_str = str(value) if not isinstance(value, (str, datetime)) else value
                                if isinstance(value_str, str):
                                    dt = parse(value_str)
                                    if dt.tzinfo is not None:
                                        dt = dt.replace(tzinfo=None)
                                    value = dt
                            except (ValueError, TypeError):
                                print(f"⚠️ Warning: Could not parse datetime for key '{key}', value '{value}'. Setting to None.")
                                value = None
                        
                        # Handle JSON fields (custom_fields, tags)
                        elif key in ['custom_fields', 'tags']:
                            if isinstance(value, str):
                                try:
                                    value = json.loads(value)
                                except (json.JSONDecodeError, TypeError):
                                    print(f"⚠️ Warning: Could not parse JSON string for key '{key}', value '{value[:100]}...'. Setting to {{}}.")
                                    value = {}
                            elif value is None:
                                value = {} # Default to empty JSON object for JSONB if API sends null
                        
                        # Handle Float fields specifically if API might send non-convertible strings not caught by general empty string rule
                        elif isinstance(model_column_type, sqltypes.Float) and isinstance(value, str):
                            try:
                                value = float(value)
                            except ValueError:
                                print(f"⚠️ Warning: Could not convert string '{value}' to float for key '{key}'. Setting to None.")
                                value = None
                        
                        # Handle Integer fields (if any in future, e.g. quantity if it were Integer)
                        elif isinstance(model_column_type, sqltypes.Integer) and isinstance(value, str):
                            try:
                                value = int(value)
                            except ValueError:
                                print(f"⚠️ Warning: Could not convert string '{value}' to int for key '{key}'. Setting to None.")
                                value = None

                    pkg_data[key] = value

                package_id_val = pkg_data.get("package_id")
                if not package_id_val:
                    print(f"⚠️ Warning: Skipping package due to missing 'package_id'. Data: {package_payload}")
                    continue

                result = await db.execute(
                    select(Package).filter_by(package_id=package_id_val)
                )
                db_package = result.scalars().first()

                if db_package:
                    for attr_key, attr_value in pkg_data.items():
                        if hasattr(db_package, attr_key):
                            setattr(db_package, attr_key, attr_value)
                else:
                    db_package = Package(**pkg_data)
                    db.add(db_package)
                processed_count += 1
            
            await db.commit()
            print(f"✅ Successfully processed and committed {processed_count} packages.")
        except Exception as e:
            await db.rollback()
            print(f"❌ Error while inserting/updating packages into database: {e}")
            traceback.print_exc()

async def sync_packages():
    """Complete sync workflow for packages"""
    print("🚀 Starting package synchronization...")
    packages_data = await fetch_packages()
    if packages_data: # Only attempt to insert if data was fetched
        await insert_packages_to_db(packages_data)
    else:
        print("ℹ️ No packages fetched, skipping database insertion.")
    print("🏁 Package synchronization finished.")