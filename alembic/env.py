"""Alembic environment configuration for AI-IMUTIS backend."""
from __future__ import annotations

import sys
import os
from pathlib import Path
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine.url import make_url
from sqlalchemy.exc import ArgumentError
from dotenv import load_dotenv

# Ensure project root on path for "app" imports when running Alembic directly
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.models import Base

# Load .env if present
load_dotenv()

# Interpret the config file for Python logging.
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Override sqlalchemy.url from environment  
database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise RuntimeError("DATABASE_URL is not set")

# Trim quotes/whitespace that sometimes sneak in from .env parsing
database_url = database_url.strip().strip("\"").strip("'")

# Validate early so the error message is actionable
try:
    make_url(database_url)
except ArgumentError as exc:
    raise RuntimeError(f"Invalid DATABASE_URL value: {database_url}") from exc

# Must set via config.set_main_option so Alembic properly expands it in the section dict
config.set_main_option("sqlalchemy.url", database_url)

# Use model metadata for autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
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
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
