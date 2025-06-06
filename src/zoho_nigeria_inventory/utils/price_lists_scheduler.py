from apscheduler.schedulers.asyncio import AsyncIOScheduler
import traceback
from src.zoho_nigeria_inventory.services.price_lists_services import fetch_price_lists, insert_price_lists_to_db

scheduler = AsyncIOScheduler()

# Scheduled sync task
async def price_lists_scheduled_sync():
    print("Running scheduled price  sync...")
    try:
        items = await fetch_price_lists()
        #test= await insert_composite_items_to_db(items)
        await insert_price_lists_to_db(items)
        #print(test)
        print("Sync with price lists successful .")
    except Exception as e:
        #print(f"Error during composite items sync: {e}")
        print(f"Error during composite items sync:")
        traceback.print_exc()