from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy.pool import NullPool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values in the .ini file in use.
config = context.config

# --- Alembic/App Integration ---
# Import your app's settings and models.
# This assumes the alembic command is run from the /app directory in the container.
from core.config import settings
from models.base import Base
from models.core import Project, Document, Measurement # Import all models

# Set the database URL from your application settings
config.set_main_option("sqlalchemy.url", str(settings.DATABASE_URL))

# Set the target metadata for autogenerate
target_metadata = Base.metadata
# --- End Integration ---


# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # The connectable is created from the sqlalchemy.url in the config
    connectable = context.config.attributes.get("connection", None)

    if connectable is None:
        connectable = engine_from_config(
            config.get_section(config.config_main_section, {}),
            prefix="sqlalchemy.",
            poolclass=NullPool,
        )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()