from apscheduler.schedulers.asyncio import AsyncIOScheduler
import traceback
from src.zoho_nigeria_inventory.services.composite_items_services import fetch_composite_items, insert_composite_items_to_db

scheduler = AsyncIOScheduler()

# Scheduled sync task
async def composite_scheduled_sync():
    print("Running scheduled composite items  sync...")
    try:
        items = await fetch_composite_items()
        #test= await insert_composite_items_to_db(items)
        await insert_composite_items_to_db(items)
        #print(test)
        print("Sync with composite items successful successful.")
    except Exception as e:
        #print(f"Error during composite items sync: {e}")
        print(f"Error during composite items sync:")
        traceback.print_exc()