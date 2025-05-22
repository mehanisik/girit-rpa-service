import os
from sqlalchemy import create_engine, NullPool
from .config import settings

engine_args = {}
if os.getenv("USE_PGBOUNCER_TRANSACTION_MODE", "false").lower() == "true":
    engine_args['poolclass'] = NullPool

# We only need the engine URI for Flask-SQLAlchemy to configure itself.
# Flask-SQLAlchemy will create its own engine and session management.
SQLALCHEMY_DATABASE_URL = settings.SQLALCHEMY_DATABASE_URI

# Base for models will be provided by Flask-SQLAlchemy's db object
# Base = declarative_base() is not strictly needed here if all models inherit from db.Model