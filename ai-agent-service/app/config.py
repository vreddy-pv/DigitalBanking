from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Anthropic
    anthropic_api_key: str = "sk-ant-missing"
    model: str = "claude-sonnet-4-6"
    max_tokens: int = 4096

    # Backend service URLs (used by InvestigationWorker)
    auth_service_url: str = "http://localhost:8001"
    account_service_url: str = "http://localhost:8002"
    transaction_service_url: str = "http://localhost:8003"
    ledger_service_url: str = "http://localhost:8004"
    complaint_service_url: str = "http://localhost:8011"
    loan_service_url: str = "http://localhost:8012"
    ops_service_url: str = "http://localhost:8013"

    # MCP Adapter layer URLs (used by specialist agents)
    casa_mcp_url: str = "http://localhost:8014"
    ml_mcp_url: str = "http://localhost:8015"
    cul_mcp_url: str = "http://localhost:8016"
    complaint_mcp_url: str = "http://localhost:8017"

    # RabbitMQ
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"

    # Redis
    redis_url: str = "redis://localhost:6379"
    session_ttl_seconds: int = 1800
    max_conversation_turns: int = 10

    # Server
    port: int = 8010

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
