from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://audit_user:password@localhost:5432/audit_db"

    # RabbitMQ
    rabbitmq_url: str = "amqp://guest:guest@rabbitmq:5672/"
    rabbitmq_queue: str = "audit_events"
    rabbitmq_exchange: str = "banking.events"
    rabbitmq_routing_key: str = "transaction.created"

    # Service
    service_name: str = "audit-service"
    service_port: int = 8009
    service_host: str = "0.0.0.0"
    env: str = "development"

    # Logging
    log_level: str = "INFO"

    model_config = {"env_file": ".env", "case_sensitive": False}


settings = Settings()
