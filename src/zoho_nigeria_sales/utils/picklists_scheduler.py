from apscheduler.schedulers.asyncio import AsyncIOScheduler
import traceback
from src.zoho_nigeria_sales.services.picklists_services import sync_picklists

scheduler = AsyncIOScheduler()

async def picklists_scheduled_sync():
    """Scheduled task to sync picklists from Zoho to database"""
    print("Running scheduled picklists sync...")
    try:
        await sync_picklists()
        print("picklists sync completed successfully.")
    except Exception as e:
        print("Error during picklists sync:")
        traceback.print_exc()
