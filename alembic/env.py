from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os

# Interpret the config file for Python logging.
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
from app.db.database import engine
from app.models import Base  # noqa

target_metadata = Base.metadata

def run_migrations_offline():
    url = os.environ.get("DATABASE_URL", "sqlite+pysqlite:///./dev.db")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
