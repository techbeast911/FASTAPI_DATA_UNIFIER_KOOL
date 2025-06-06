from apscheduler.schedulers.asyncio import AsyncIOScheduler
import traceback
from src.zoho_nigeria_purchases.services.purchase_orders_services import sync_purchase_orders



scheduler = AsyncIOScheduler()


async def purchase_orders_sync():
    print("Running scheduled purchase orders sync...")
    try:
        await sync_purchase_orders()
        print("Purchase orders sync completed successfully.")
    except Exception as e:
        print("Error during Purchase orders sync:")
        traceback.print_exc()