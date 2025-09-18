from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import make_url

from app.core.config import settings

def create_database_engine(database_url: str):
    """
    Create an async SQLAlchemy engine, correctly handling the 'schema' parameter
    for the asyncpg driver.
    """
    db_url = make_url(database_url)
    connect_args = {}

    # asyncpg doesn't support 'schema' in the DSN, so we move it to connect_args
    if db_url.drivername.startswith("postgresql+asyncpg") and db_url.query.get("schema"):
        schema = db_url.query["schema"]
        connect_args["server_settings"] = {"search_path": schema}
        # Create a new URL object without the schema query parameter
        db_url = db_url.set(query={k: v for k, v in db_url.query.items() if k != "schema"})

    return create_async_engine(db_url, pool_pre_ping=True, connect_args=connect_args)

engine = create_database_engine(settings.DATABASE_URL)

AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
 )