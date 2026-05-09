from sqlalchemy import create_engine
from app.config import settings

# Two separate SQLAlchemy engines — read-only access
transaction_engine = create_engine(settings.transaction_db_url, pool_pre_ping=True)
ledger_engine = create_engine(settings.ledger_db_url, pool_pre_ping=True)


def get_transaction_db():
    with transaction_engine.connect() as conn:
        yield conn


def get_ledger_db():
    with ledger_engine.connect() as conn:
        yield conn
