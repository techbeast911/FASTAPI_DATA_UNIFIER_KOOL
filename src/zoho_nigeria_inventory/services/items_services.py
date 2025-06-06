import httpx
from sqlalchemy import select
from src.config import CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN, ORG_ID
from src.zoho_nigeria_inventory.db.database import async_session
from src.zoho_nigeria_inventory.models.models_items import Item

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


async def fetch_items():
    token = await get_access_token()
    page = 1
    all_items = []

    async with httpx.AsyncClient() as client:
        while True:
            url = "https://inventory.zoho.com/api/v1/items"
            headers = {"Authorization": f"Zoho-oauthtoken {token}"}
            params = {"organization_id": ORG_ID, "page": page}

            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            items = data.get("items", [])

            if not items:
                break

            all_items.extend(items)
            page += 1

    print(f"Fetched {len(all_items)} items from Zoho")
    return all_items


async def insert_items_to_db(items):
    print("Inserting items into database...")
    async with async_session() as db:
        try:
            for item in items:
                item_data = {}
                for key, value in item.items():
                    if not hasattr(Item, key):
                        continue
                    column_type = getattr(Item, key).type
                    if isinstance(value, str) and value.strip() == "":
                        try:
                            if issubclass(column_type.python_type, (int, float)):
                                value = None
                        except NotImplementedError:
                            pass
                    item_data[key] = value

                result = await db.execute(select(Item).filter_by(item_id=item_data["item_id"]))
                db_item = result.scalars().first()

                if db_item:
                    for key, value in item_data.items():
                        setattr(db_item, key, value)
                else:
                    db_item = Item(**item_data)
                    db.add(db_item)

            await db.commit()
            print(f"Successfully inserted/updated {len(items)} items")
        except Exception as e:
            await db.rollback()
            print(f"Error while inserting into database: {e}")
