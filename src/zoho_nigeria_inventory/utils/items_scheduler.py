from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.zoho_nigeria_inventory.services.items_services import fetch_items, insert_items_to_db

scheduler = AsyncIOScheduler()

# Scheduled sync task
async def scheduled_sync():
    print("Running scheduled sync...")
    try:
        items = await fetch_items()
        test= await insert_items_to_db(items)
        print(test)
        print("Sync successful.")
    except Exception as e:
        print(f"Error during sync: {e}")