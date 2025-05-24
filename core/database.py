import os
from sqlalchemy import create_engine, NullPool
from .config import settings

engine_args = {}
if os.getenv("USE_PGBOUNCER_TRANSACTION_MODE", "false").lower() == "true":
    engine_args['poolclass'] = NullPool

SQLALCHEMY_DATABASE_URL = settings.SQLALCHEMY_DATABASE_URI
