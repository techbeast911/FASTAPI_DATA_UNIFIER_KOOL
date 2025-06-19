from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from src.db.main import initdb
from src.zoho_nigeria_inventory.routes.items_routes import router as api_router
from src.zoho_nigeria_inventory.db.database import async_session, init_db
from src.zoho_nigeria_inventory.utils.items_scheduler import scheduled_sync
from src.zoho_nigeria_inventory.utils.composite_items_scheduler import composite_scheduled_sync
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.zoho_nigeria_inventory.utils.price_lists_scheduler import price_lists_scheduled_sync
from src.zoho_nigeria_inventory.utils.inventory_adjustments_scheduler import sync_inventory_adjustments
from src.zoho_nigeria_sales.utils.customers_scheduler import customers_scheduled_sync
from src.zoho_nigeria_sales.utils.invoices_scheduler import invoices_scheduled_sync
from src.zoho_nigeria_sales.utils.packages_scheduler import packages_scheduled_sync
from src.zoho_nigeria_sales.utils.picklists_scheduler import picklists_scheduled_sync
from src.zoho_nigeria_sales.utils.sales_orders_scheduler import sales_orders_scheduled_sync
from src.zoho_nigeria_purchases.utils.vendors_scheduler import vendors_scheduled_sync
from src.zoho_nigeria_purchases.utils.purchase_orders_scheduler import purchase_orders_sync
from src.kool_assembly.routes.routes_batteries import battery_router




#lifespan event
@asynccontextmanager
async def lifespan(app:FastAPI):
    await initdb()
    yield
    print("server is stopping") 

version = 'v1'

app = FastAPI(
    title="Kool Data Hub",
    description="A REST API for Koolboks data web service",
    version= version,
    lifespan=lifespan
)

scheduler = AsyncIOScheduler()

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routes
app.include_router(api_router)
app.include_router(battery_router, prefix=f"/api/{version}/battery", tags=['battery'])
# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_event():
    await init_db()
    scheduler.start()
    # scheduler.add_job(scheduled_sync, "cron", hour=13, minute=0)
    scheduler.add_job(scheduled_sync,trigger="cron", minute='*/1')
    # scheduler.add_job(composite_scheduled_sync, "cron", hour=14, minute=0)
    # scheduler.add_job(price_lists_scheduled_sync, "cron", hour=15, minute=0)
    # scheduler.add_job(sync_inventory_adjustments, "cron", hour=16, minute=0)
    # scheduler.add_job(customers_scheduled_sync, "cron", hour=17, minute=0)
    # scheduler.add_job(invoices_scheduled_sync, "cron", hour=18, minute=0)
    # scheduler.add_job(packages_scheduled_sync, "cron", hour=19, minute=0)
    # scheduler.add_job(picklists_scheduled_sync, "cron", hour=23, minute=0)
    # scheduler.add_job(sales_orders_scheduled_sync, "cron", hour=21, minute=0)
    scheduler.add_job(vendors_scheduled_sync, "cron",hour = 12, minute=22)
    scheduler.add_job(purchase_orders_sync, "cron", hour=15, minute=44)
    print("Database initialized and scheduler started.")
    print("Scheduler started and jobs added.")