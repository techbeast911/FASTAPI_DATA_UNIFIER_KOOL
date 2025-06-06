from apscheduler.schedulers.asyncio import AsyncIOScheduler
import traceback
from src.zoho_nigeria_inventory.services.inventory_adjustments_services import fetch_inventory_adjustments, insert_inventory_adjustments_to_db

scheduler = AsyncIOScheduler()

# Scheduled sync task
async def sync_inventory_adjustments():
    print("Running scheduled composite items  sync...")
    try:
        adjustments = await fetch_inventory_adjustments()
        await insert_inventory_adjustments_to_db(adjustments)
        print("Sync with composite items successful successful.")
    except Exception as e:
        #print(f"Error during composite items sync: {e}")
        print(f"Error during composite items sync:")
        traceback.print_exc()