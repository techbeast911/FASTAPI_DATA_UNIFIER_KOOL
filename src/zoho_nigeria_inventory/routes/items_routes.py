from fastapi import APIRouter
from fastapi.responses import JSONResponse, HTMLResponse
from sqlalchemy import select
from src.zoho_nigeria_inventory.db.database import async_session
from src.zoho_nigeria_inventory.models.models_items import Item
from src.zoho_nigeria_inventory.services.items_services import fetch_items, insert_items_to_db
from src.zoho_nigeria_inventory.utils.items_serializer import serialize_model

router = APIRouter()

@router.get("/")
async def get_html():
    with open("static/index.html", "r") as f:
        return HTMLResponse(f.read())

@router.get("/sync")
async def manual_sync():
    try:
        items = await fetch_items()
        await insert_items_to_db(items)
        return {"status": "success", "message": "Manual sync completed"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/items")
async def get_items():
    async with async_session() as db:
        result = await db.execute(select(Item))
        items = result.scalars().all()
        return JSONResponse([serialize_model(item) for item in items])
