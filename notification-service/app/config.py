from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://notification_user:password@localhost:5432/notification_db"

    # RabbitMQ
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    rabbitmq_queue: str = "transaction_events"

    # SMTP
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str
    smtp_password: str
    smtp_from: str = "noreply@digitalbanking.com"

    # Service
    service_name: str = "notification-service"
    service_port: int = 8006
    service_host: str = "0.0.0.0"
    env: str = "development"

    # Logging
    log_level: str = "INFO"

    # Retry
    max_retry_attempts: int = 3
    retry_backoff_seconds: int = 5

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
