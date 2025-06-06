import httpx
from sqlalchemy import select
from src.config import CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN, ORG_ID
from src.zoho_nigeria_inventory.db.database import async_session
from src.zoho_nigeria_inventory.models.models_composite_items import CompositeItem
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


async def fetch_composite_items():
    token = await get_access_token()
    page = 1
    all_items = []

    async with httpx.AsyncClient() as client:
        while True:
            url = "https://inventory.zoho.com/api/v1/compositeitems"
            headers = {"Authorization": f"Zoho-oauthtoken {token}"}
            params = {"organization_id": ORG_ID, "page": page}

            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            composite_items = data.get("composite_items", [])

            if not composite_items:
                break

            all_items.extend(composite_items)
            page += 1

    print(f"Fetched {len(all_items)} items from Zoho")
    return all_items


async def insert_composite_items_to_db(items):
    print("Inserting composite items into database...")
    async with async_session() as db:
        try:
            for item in items:
                item_data = {}
                for key, value in item.items():
                    if not hasattr(CompositeItem, key):
                        continue
                    column_type = getattr(CompositeItem, key).type
                    if isinstance(value, str) and value.strip() == "":
                        try:
                            if issubclass(column_type.python_type, (int, float)):
                                value = None
                        except NotImplementedError:
                            pass
                    item_data[key] = value

                result = await db.execute(select(CompositeItem).filter_by(composite_item_id=item_data["composite_item_id"]))
                db_item = result.scalars().first()

                if db_item:
                    for key, value in item_data.items():
                        setattr(db_item, key, value)
                else:
                    db_item = CompositeItem(**item_data)
                    db.add(db_item)

            await db.commit()
            print(f"Successfully inserted/updated {len(items)} items")
        except Exception as e:
            await db.rollback()
            #print(f"Error while inserting into database: {e}")
            print(f"Error while inserting into database:")

            traceback.print_exc()

