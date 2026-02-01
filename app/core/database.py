from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# 1. Create the Base for models
Base = declarative_base()

# 2. Auto-Fix the URL (Swap postgresql:// for postgresql+asyncpg://)
database_url = settings.DATABASE_URL
if database_url and database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

# 3. Create the Async Engine
engine = create_async_engine(database_url, echo=False, future=True)

# 4. Create the Session
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# 5. Dependency for API endpoints
async def get_db():
    async with async_session() as session:
        yield session
