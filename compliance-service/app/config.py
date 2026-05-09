from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://compliance_user:password@postgres:5432/compliance_db"
    rabbitmq_url: str = "amqp://guest:guest@rabbitmq:5672/"
    rabbitmq_queue: str = "compliance_events"
    rabbitmq_exchange: str = "banking.events"
    rabbitmq_routing_key: str = "transaction.created"
    service_port: int = 8008
    service_host: str = "0.0.0.0"
    log_level: str = "INFO"
    env: str = "development"

    # AML thresholds (configurable)
    high_value_threshold: float = 50000.0       # Single transaction alert
    large_withdrawal_threshold: float = 25000.0  # Withdrawal alert
    frequent_tx_window_minutes: int = 60         # Window for frequency check
    frequent_tx_count: int = 5                   # Transactions in window = alert
    rapid_tx_window_minutes: int = 10            # Window for rapid check
    rapid_tx_count: int = 3                      # Transactions in rapid window = alert
    structuring_lower: float = 40000.0           # Structuring lower bound
    structuring_upper: float = 49999.0           # Structuring upper bound
    structuring_count: int = 3                   # Structuring transaction count

    model_config = {"env_file": ".env", "case_sensitive": False}


settings = Settings()
