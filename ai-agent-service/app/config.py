from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Anthropic
    anthropic_api_key: str = "sk-ant-missing"
    model: str = "claude-sonnet-4-6"
    max_tokens: int = 4096

    # Backend service URLs
    auth_service_url: str = "http://localhost:8001"
    account_service_url: str = "http://localhost:8002"
    transaction_service_url: str = "http://localhost:8003"
    ledger_service_url: str = "http://localhost:8004"

    # Redis
    redis_url: str = "redis://localhost:6379"
    session_ttl_seconds: int = 1800
    max_conversation_turns: int = 10

    # Server
    port: int = 8010

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
