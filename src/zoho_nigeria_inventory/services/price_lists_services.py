import httpx
from sqlalchemy import select
import asyncio
from src.config import CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN, ORG_ID
from src.zoho_nigeria_inventory.db.database import async_session
from src.zoho_nigeria_inventory.models.models_price_lists import PriceList
import traceback

# Zoho Auth and Fetch
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


async def fetch_price_lists():
    token = await get_access_token()
    page = 1
    per_page = 200  # Max allowed by Zoho API
    all_items = []

    async with httpx.AsyncClient() as client:
        while True:
            url = "https://inventory.zoho.com/api/v1/pricebooks"
            headers = {"Authorization": f"Zoho-oauthtoken {token}"}
            params = {
                "organization_id": ORG_ID,
                "page": page,
                "per_page": per_page  # Added pagination parameter
            }

            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            price_lists = data.get("pricebooks", [])

            if not price_lists:
                break

            all_items.extend(price_lists)
            
            # Improved pagination check - stop if we got fewer items than requested
            if len(price_lists) < per_page:
                break
                
            page += 1
            await asyncio.sleep(0.5)  # Add small delay between requests

    print(f"Fetched {len(all_items)} price lists from Zoho")
    return all_items


async def insert_price_lists_to_db(items):
    print("Inserting price lists into database...")
    async with async_session() as db:
        try:
            for item in items:
                item_data = {}
                for key, value in item.items():
                    if not hasattr(PriceList, key):  # Changed from CompositeItem to PriceList
                        continue
                    column_type = getattr(PriceList, key).type
                    if isinstance(value, str) and value.strip() == "":
                        try:
                            if issubclass(column_type.python_type, (int, float)):
                                value = None
                        except NotImplementedError:
                            pass
                    item_data[key] = value

                # Changed filter to use pricebook_id instead of composite_item_id
                result = await db.execute(select(PriceList).filter_by(pricebook_id=item_data["pricebook_id"]))
                db_item = result.scalars().first()

                if db_item:
                    for key, value in item_data.items():
                        setattr(db_item, key, value)
                else:
                    db_item = PriceList(**item_data)  # Changed from CompositeItem to PriceList
                    db.add(db_item)

            await db.commit()
            print(f"Successfully inserted/updated {len(items)} items")
        except Exception as e:
            await db.rollback()
            print(f"Error while inserting into database: {e}")
            traceback.print_exc()

