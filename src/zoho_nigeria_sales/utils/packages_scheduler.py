from apscheduler.schedulers.asyncio import AsyncIOScheduler
import traceback
from src.zoho_nigeria_sales.services.packages_services import sync_packages

scheduler = AsyncIOScheduler()

async def packages_scheduled_sync():
    """Scheduled task to sync packages from Zoho to database"""
    print("Running scheduled packages sync...")
    try:
        await sync_packages()
        print("packages sync completed successfully.")
    except Exception as e:
        print("Error during invoices sync:")
        traceback.print_exc()
