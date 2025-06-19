# from sqlalchemy.ext.asyncio import create_async_engine
# from sqlalchemy import text
# from src.config import Config
# from sqlmodel import SQLModel
# from sqlalchemy.ext.asyncio import AsyncEngine
# from sqlmodel import create_engine, text
# from src.kool_assembly.models.models_battery import Battery
# from src.kool_assembly.models.models_inventory_in import Inventory_in
# from src.kool_assembly.models.models_inventory_return import Inventory_return
# from src.kool_assembly.models.models_inverters import Inverters
# from src.kool_assembly.models.models_iot import Iot
# from src.kool_assembly.models.models_paygo import Paygo
# from src.kool_assembly.models.models_production import Production
# from src.kool_assembly.models.models_quality import Quality


# engine = AsyncEngine(create_engine(
#     url=Config.DATABASE_URL,
#     echo=True
# ))





# async def initdb():
#     """create our database models in the database"""

#     async with engine.begin() as conn:
#         await conn.execute(text("CREATE SCHEMA IF NOT EXISTS kool_assembly"))
#         await conn.execute(text("CREATE SCHEMA IF NOT EXISTS maintenance"))
#         await conn.run_sync(SQLModel.metadata.create_all)


from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker # Import AsyncSession and async_sessionmaker
from sqlalchemy import text
from src.config import Config
from sqlmodel import SQLModel
# from sqlalchemy.ext.asyncio import AsyncEngine # AsyncEngine is generally not needed for create_async_engine
# from sqlmodel import create_engine, text # create_engine is for sync, use create_async_engine

# Import all your SQLModel models to ensure they are registered with SQLModel.metadata
from src.kool_assembly.models.models_battery import Battery
from src.kool_assembly.models.models_inventory_in import Inventory_in
from src.kool_assembly.models.models_inventory_return import Inventory_return
from src.kool_assembly.models.models_inverters import Inverters
from src.kool_assembly.models.models_iot import Iot
from src.kool_assembly.models.models_paygo import Paygo
from src.kool_assembly.models.models_production import Production
from src.kool_assembly.models.models_quality import Quality


# Create async engine
# Use create_async_engine directly, not AsyncEngine(create_engine(...))
engine = create_async_engine(
    Config.DATABASE_URL,
    echo=True, # Set to True for verbose logging of SQL queries
    future=True # Recommended for SQLAlchemy 2.0 style operations
)

# Create an async session factory
# This will be used to create new session instances for each request
async_session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False, # Prevents objects from expiring after commit, useful for FastAPI responses
    class_=AsyncSession # Specify the session class as AsyncSession
)

# Dependency to get a database session for FastAPI routes
async def get_session():
    """
    Dependency function to provide an asynchronous database session.
    This function yields a session, ensuring it's properly closed after use.
    """
    async with async_session() as session:
        yield session


async def initdb(): # Renamed from initdb to init_db for consistency with main.py
    """
    Creates database schemas and tables based on SQLModel metadata.
    """
    async with engine.begin() as conn:
        # Create schemas if they don't exist
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS kool_assembly"))
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS maintenance"))

        # Run SQLModel's metadata.create_all to create all defined tables
        # within the established schemas.
        # This requires all SQLModel models to be imported somewhere
        # before init_db() is called.
        await conn.run_sync(SQLModel.metadata.create_all)
