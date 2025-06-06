from apscheduler.schedulers.asyncio import AsyncIOScheduler
import traceback
from src.zoho_nigeria_sales.services.invoices_services import sync_invoices

scheduler = AsyncIOScheduler()

async def invoices_scheduled_sync():
    """Scheduled task to sync invoices from Zoho to database"""
    print("Running scheduled invoices sync...")
    try:
        await sync_invoices()
        print("Invoices sync completed successfully.")
    except Exception as e:
        print("Error during invoices sync:")
        traceback.print_exc()
