import httpx
from sqlalchemy import select
from src.config import CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN, ORG_ID
from src.zoho_nigeria_inventory.db.database import async_session
from src.zoho_nigeria_inventory.models.models_inventory_adjustments import InventoryAdjustment
import traceback
import asyncio

# Zoho Auth (same as before)
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

async def fetch_inventory_adjustments():
    token = await get_access_token()
    page = 1
    per_page = 200  # Zoho's max per page
    all_adjustments = []

    async with httpx.AsyncClient() as client:
        while True:
            url = "https://inventory.zoho.com/api/v1/inventoryadjustments"
            headers = {
                "Authorization": f"Zoho-oauthtoken {token}",
                "X-com-zoho-inventory-organizationid": ORG_ID
            }
            params = {
                "organization_id": ORG_ID,
                "page": page,
                "per_page": per_page
            }

            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            adjustments = data.get("inventory_adjustments", [])

            if not adjustments:
                break

            all_adjustments.extend(adjustments)
            
            # Improved pagination check
            if len(adjustments) < per_page:
                break
                
            page += 1
            await asyncio.sleep(0.5)  # Rate limiting

    print(f"Fetched {len(all_adjustments)} inventory adjustments from Zoho")
    return all_adjustments

# async def insert_inventory_adjustments_to_db(adjustments):
#     print("Inserting inventory adjustments into database...")
#     async with async_session() as db:
#         try:
#             for adjustment in adjustments:
#                 adj_data = {}
#                 for key, value in adjustment.items():
#                     if not hasattr(InventoryAdjustment, key):
#                         continue
                    
#                     # Handle empty strings for numeric fields
#                     column_type = getattr(InventoryAdjustment, key).type
#                     if isinstance(value, str) and value.strip() == "":
#                         try:
#                             if issubclass(column_type.python_type, (int, float)):
#                                 value = None
#                         except NotImplementedError:
#                             pass
                    
#                     # Handle custom fields if present
#                     if key == "custom_fields" and value:
#                         # Process individual custom fields if needed
#                         pass
                    
#                     adj_data[key] = value

#                 # Check if adjustment exists
#                 result = await db.execute(
#                     select(InventoryAdjustment).filter_by(
#                         inventory_adjustment_id=adj_data["inventory_adjustment_id"]
#                     )
#                 )
#                 db_adj = result.scalars().first()

#                 if db_adj:
#                     # Update existing adjustment
#                     for key, value in adj_data.items():
#                         setattr(db_adj, key, value)
#                 else:
#                     # Create new adjustment
#                     db_adj = InventoryAdjustment(**adj_data)
#                     db.add(db_adj)

#             await db.commit()
#             print(f"Successfully inserted/updated {len(adjustments)} inventory adjustments")
#         except Exception as e:
#             await db.rollback()
#             print(f"Error while inserting into database: {e}")
#             traceback.print_exc()

async def insert_inventory_adjustments_to_db(adjustments):
    print("Inserting inventory adjustments into database...")
    async with async_session() as db:
        try:
            for adjustment in adjustments:
                adj_data = {}
                for key, value in adjustment.items():
                    if not hasattr(InventoryAdjustment, key):
                        continue
                    
                    # Handle custom fields and custom_field_hash specially
                    if key == "custom_field_hash":
                        # Convert dict to string if necessary
                        if isinstance(value, dict):
                            value = str(value)
                    
                    if key == "custom_fields":
                        # Ensure custom_fields is properly formatted JSON
                        if isinstance(value, str):
                            try:
                                value = json.loads(value)
                            except json.JSONDecodeError:
                                value = None
                    
                    # Handle empty strings for numeric fields
                    column_type = getattr(InventoryAdjustment, key).type
                    if isinstance(value, str) and value.strip() == "":
                        try:
                            if issubclass(column_type.python_type, (int, float)):
                                value = None
                        except NotImplementedError:
                            pass
                    
                    adj_data[key] = value

                # Check if adjustment exists
                result = await db.execute(
                    select(InventoryAdjustment).filter_by(
                        inventory_adjustment_id=adj_data["inventory_adjustment_id"]
                    )
                )
                db_adj = result.scalars().first()

                if db_adj:
                    # Update existing adjustment
                    for key, value in adj_data.items():
                        setattr(db_adj, key, value)
                else:
                    # Create new adjustment
                    db_adj = InventoryAdjustment(**adj_data)
                    db.add(db_adj)

            await db.commit()
            print(f"Successfully inserted/updated {len(adjustments)} inventory adjustments")
        except Exception as e:
            await db.rollback()
            print(f"Error while inserting into database: {e}")
            traceback.print_exc()