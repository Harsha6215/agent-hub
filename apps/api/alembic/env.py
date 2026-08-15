"""
Alembic migration environment — async PostgreSQL support.

Run from monorepo root:
    cd agent-hub && alembic -c apps/api/alembic.ini upgrade head
"""

import asyncio
import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# Add monorepo root to sys.path so `apps.api.app...` imports work
monorepo_root = str(Path(__file__).resolve().parents[3])
if monorepo_root not in sys.path:
    sys.path.insert(0, monorepo_root)

from apps.api.app.core.database import Base  # noqa: E402
from apps.api.app.models import *  # noqa: E402, F401, F403 — ensure all models loaded

# Alembic Config object
config = context.config

# Override sqlalchemy.url with DATABASE_URL env var (convert asyncpg → psycopg2 for sync alembic)
database_url = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/agent_hub",
)
# Alembic runs synchronously — swap async driver for sync driver
sync_url = database_url.replace("+asyncpg", "")
config.set_main_option("sqlalchemy.url", sync_url)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode — emit SQL to stdout."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode — sync connection."""
    from sqlalchemy import engine_from_config

    configuration = config.get_section(config.config_ini_section, {})
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        do_run_migrations(connection)

    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
