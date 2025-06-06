from apscheduler.schedulers.asyncio import AsyncIOScheduler
import traceback
from src.zoho_nigeria_sales.services.customers_services import fetch_customers, insert_customers_to_db

scheduler = AsyncIOScheduler()

async def customers_scheduled_sync():
    """Scheduled task to sync customers from Zoho to database"""
    print("Running scheduled customers sync...")
    try:
        # Fetch and insert customers
        customers = await fetch_customers()
        await insert_customers_to_db(customers)
        print("Customers sync completed successfully.")
    except Exception as e:
        print(f"Error during customers sync:")
        traceback.print_exc()