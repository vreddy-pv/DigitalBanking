from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    transaction_db_url: str = "postgresql://analytics_user:password@localhost:5432/transaction_db"
    ledger_db_url: str = "postgresql://analytics_user:password@localhost:5432/ledger_db"
    service_port: int = 8007
    service_host: str = "0.0.0.0"
    log_level: str = "INFO"

    model_config = ConfigDict(env_file=".env")


settings = Settings()
