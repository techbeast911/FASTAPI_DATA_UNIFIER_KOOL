from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from src.config import DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=False)#,connect_args={
#         "server_settings": {
#             "search_path": "zoho_nigeria_inventory,public"
#         }
#     })
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
