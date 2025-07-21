# main.py - Entry point for the FastAPI application
from fastapi import FastAPI,BackgroundTasks
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


from src.db.main import initdb as main_init_db 

# Import routers
from src.zoho_nigeria_inventory.routes.items_routes import router as api_router
from src.kool_assembly.routes.routes_batteries import battery_router
from src.kool_assembly.routes.routes_inventory_in import inventory_in_router
from src.kool_assembly.routes.routes_inventory_return import inventory_return_router
from src.kool_assembly.routes.routes_inverters import inverters_router
from src.kool_assembly.routes.routes_iot import iot_router
from src.kool_assembly.routes.routes_paygo import paygo_router
from src.kool_assembly.routes.routes_production import production_router
from src.kool_assembly.routes.routes_quality import quality_router






# Import scheduler and related sync functions
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.zoho_nigeria_inventory.utils.items_scheduler import scheduled_sync
from src.zoho_nigeria_inventory.utils.composite_items_scheduler import composite_scheduled_sync
from src.zoho_nigeria_inventory.utils.price_lists_scheduler import price_lists_scheduled_sync
from src.zoho_nigeria_inventory.utils.inventory_adjustments_scheduler import sync_inventory_adjustments
from src.zoho_nigeria_sales.utils.customers_scheduler import customers_scheduled_sync
from src.zoho_nigeria_sales.utils.invoices_scheduler import invoices_scheduled_sync
from src.zoho_nigeria_sales.utils.packages_scheduler import packages_scheduled_sync
from src.zoho_nigeria_sales.utils.picklists_scheduler import picklists_scheduled_sync
from src.zoho_nigeria_sales.utils.sales_orders_scheduler import sales_orders_scheduled_sync
from src.zoho_nigeria_purchases.utils.vendors_scheduler import vendors_scheduled_sync
from src.zoho_nigeria_purchases.utils.purchase_orders_scheduler import purchase_orders_sync
from src.auth.auth_routes import auth_router
from .middleware import register_middleware


# lifespan event
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Initializes the database on startup and performs cleanup on shutdown.
    """
    print("Initializing database...")
    # Call the main database initialization function
    await main_init_db() # Using the aliased function name
    print("Database initialized.")
    yield
    print("Server is stopping.")


version = 'v1'

app = FastAPI(
    title="Kool Data Hub",
    description="A REST API for Koolboks data web service",
    version=version,
    lifespan=lifespan # Use the lifespan context manager
)

register_middleware(app)  # Register custom middleware for logging

scheduler = AsyncIOScheduler()




# Routes

app.include_router(api_router, prefix=f"/api/{version}/items", tags=['Items']) # Assuming api_router is for "items"
app.include_router(battery_router, prefix=f"/api/{version}/batteries", tags=['Batteries']) 
app.include_router(auth_router, prefix=f"/api/{version}/auth", tags=['Auth'])  
app.include_router(inventory_in_router, prefix=f"/api/{version}/inventory-in", tags=['Inventory In'])  # Inventory In routes
app.include_router(inventory_return_router, prefix=f"/api/{version}/inventory-return", tags=['Inventory Return'])  # Inventory Return routes
app.include_router(inverters_router, prefix=f"/api/{version}/inverters",tags=["Inverters"])# Inverters routes
app.include_router(iot_router, prefix=f"/api/{version}/iot", tags=["IoT"])  # IoT routes
app.include_router(paygo_router, prefix=f"/api/{version}/paygo", tags=["Paygo"])  # Paygo routes
app.include_router(production_router, prefix=f"/api/{version}/production", tags=["Production"])  # Production routes
app.include_router(quality_router, prefix=f"/api/{version}/quality", tags=["Quality"])  # Quality routes

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
async def startup_event():
    """
    Handles tasks to run when the application starts up, like scheduling jobs.
    Database initialization is now handled by the lifespan event, so no redundant call here.
    """
    # Removed the redundant init_db call from here.
    # The database init is now solely managed by the lifespan event.

    scheduler.start()
    scheduler.add_job(scheduled_sync, trigger="cron", minute='*/1')
    # scheduler.add_job(composite_scheduled_sync, "cron", hour=14, minute=0)
    # scheduler.add_job(price_lists_scheduled_sync, "cron", hour=15, minute=0)
    # scheduler.add_job(sync_inventory_adjustments, "cron", hour=16, minute=0)
    # scheduler.add_job(customers_scheduled_sync, "cron", hour=17, minute=0)
    # scheduler.add_job(invoices_scheduled_sync, "cron", hour=18, minute=0)
    # scheduler.add_job(packages_scheduled_sync, "cron", hour=19, minute=0)
    # scheduler.add_job(picklists_scheduled_sync, "cron", hour=23, minute=0)
    # scheduler.add_job(sales_orders_scheduled_sync, "cron", hour=21, minute=0)
    scheduler.add_job(vendors_scheduled_sync, "cron", hour=12, minute=22)
    scheduler.add_job(purchase_orders_sync, "cron", hour=15, minute=44)
    print("Scheduler started and jobs added.")
