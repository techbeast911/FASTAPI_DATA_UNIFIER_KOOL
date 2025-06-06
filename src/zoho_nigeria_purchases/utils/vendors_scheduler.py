from apscheduler.schedulers.asyncio import AsyncIOScheduler
import traceback
from src.zoho_nigeria_purchases.services.vendors_services import sync_vendors

scheduler = AsyncIOScheduler()

async def vendors_scheduled_sync():
    """Scheduled task to sync vendors from Zoho to database"""
    print("Running scheduled vendors sync...")
    try:
        await sync_vendors()
        print("Vendors sync completed successfully.")
    except Exception as e:
        print("Error during vendors sync:")
        traceback.print_exc()