from apscheduler.schedulers.asyncio import AsyncIOScheduler
import traceback
from src.zoho_nigeria_sales.services.sales_orders_services import sync_sales_orders

scheduler = AsyncIOScheduler()

async def sales_orders_scheduled_sync():
    """Scheduled task to sync sales_orders from Zoho to database"""
    print("Running scheduled sales_orders sync...")
    try:
        await sync_sales_orders()
        print("sales_orders sync completed successfully.")
    except Exception as e:
        print("Error during sales_orders sync:")
        traceback.print_exc()
