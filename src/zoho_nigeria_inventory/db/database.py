from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from src.config import Config
from sqlalchemy import text

# Create async engine with optional schema search_path
engine = create_async_engine(
    Config.DATABASE_URL,
    echo=True
    
)

# Create an async session factory
async_session = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

# Define declarative base
Base = declarative_base()

# Initialize database
async def init_db():
    async with engine.begin() as conn:
        
        await conn.run_sync(Base.metadata.create_all)

