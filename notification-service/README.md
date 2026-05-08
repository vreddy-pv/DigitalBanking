# Notification Service

Async notification service for the Digital Banking Platform. Listens for transaction events and sends email/SMS notifications.

## Overview

The Notification Service is built with FastAPI and provides:

- **Async Event Processing**: Listens to `TransactionCreatedEvent` from RabbitMQ
- **Email Notifications**: Sends email via SMTP with retry logic
- **SMS Notifications**: Twilio stub implementation (ready for real integration)
- **Delivery Tracking**: Database persistence of all notifications
- **Retry Logic**: Exponential backoff (3 attempts max)
- **Health Checks**: Service health monitoring

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- RabbitMQ 3.12+

### Local Development Setup

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Configure environment**:
```bash
cp .env.example .env
# Update .env with your settings (SMTP credentials, database URL, etc.)
```

3. **Run Alembic migrations**:
```bash
alembic upgrade head
```

4. **Start the service**:
```bash
uvicorn app.main:app --reload --port 8006
```

The service will be available at `http://localhost:8006`

### Docker Development

The notification service is included in the docker-compose.yml. To start all services:

```bash
docker-compose up -d
```

## Architecture

```
FastAPI Application
├─ Event Listener (RabbitMQ consumer)
│  └─ Consumes TransactionCreatedEvent
├─ Notification Service (business logic)
│  ├─ Email template rendering
│  ├─ SMS formatting
│  └─ Notification composition
├─ Delivery Engines
│  ├─ SMTP Email Provider
│  └─ Twilio SMS Stub (mock)
├─ Database (PostgreSQL)
│  └─ Notifications table with audit trail
└─ Health Checks
   └─ GET /health → Database, event listener status
```

## REST API Endpoints

### Health Check
```bash
GET /health
```

Response:
```json
{
  "status": "UP",
  "database": "UP",
  "event_listener": "LISTENING",
  "service": "notification-service"
}
```

### Get Notification
```bash
GET /api/v1/notifications/{notification_id}
```

### List Notifications
```bash
GET /api/v1/notifications?transaction_id={id}&status=SENT&limit=20&offset=0
```

### Retry Failed Notification
```bash
POST /api/v1/notifications/{notification_id}/retry
```

### Get Statistics
```bash
GET /api/v1/notifications/stats
```

Response:
```json
{
  "total_sent": 1000,
  "total_failed": 2,
  "total_pending": 5,
  "retry_queue": 5,
  "success_rate": 99.8
}
```

## Database Schema

### notifications table

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| transaction_id | UUID | Reference to transaction |
| notification_type | VARCHAR(20) | EMAIL, SMS |
| recipient | VARCHAR(255) | Email or phone number |
| subject | VARCHAR(255) | Email subject (null for SMS) |
| body | TEXT | Message content |
| status | VARCHAR(20) | PENDING, SENT, FAILED |
| attempts | INT | Number of delivery attempts |
| max_attempts | INT | Maximum retry attempts (default 3) |
| error_message | TEXT | Last error (if failed) |
| sent_at | DATETIME | Timestamp when sent |
| created_at | DATETIME | Creation timestamp |
| updated_at | DATETIME | Last update timestamp |

## Configuration

Environment variables (see .env.example):

- `DATABASE_URL`: PostgreSQL connection string
- `RABBITMQ_URL`: RabbitMQ connection string
- `RABBITMQ_QUEUE`: Event queue name
- `SMTP_HOST`: SMTP server hostname
- `SMTP_PORT`: SMTP server port
- `SMTP_USER`: SMTP authentication username
- `SMTP_PASSWORD`: SMTP authentication password
- `SMTP_FROM`: Sender email address
- `SERVICE_PORT`: Service port (default 8006)
- `SERVICE_HOST`: Service host (default 0.0.0.0)
- `ENV`: Environment (development/production)
- `LOG_LEVEL`: Logging level (default INFO)
- `MAX_RETRY_ATTEMPTS`: Max retries per notification
- `RETRY_BACKOFF_SECONDS`: Backoff delay between retries

## Testing

### Unit Tests
```bash
pytest tests/unit -v --cov=app --cov-report=html
```

### Integration Tests
```bash
pytest tests/integration -v
```

### All Tests
```bash
pytest tests/ -v --cov=app --cov-report=html
```

## Development

### Project Structure
```
notification-service/
├── app/
│  ├── main.py                    # FastAPI application
│  ├── config.py                  # Configuration
│  ├── database.py                # Database setup
│  ├── models/                    # ORM entities
│  ├── schemas/                   # Pydantic schemas
│  ├── services/                  # Business logic
│  ├── events/                    # Event handlers
│  ├── controllers/               # API endpoints
│  └── templates/                 # Email templates
├── alembic/                      # Database migrations
├── tests/                        # Test suite
├── requirements.txt              # Dependencies
├── Dockerfile                    # Docker image
└── README.md                     # This file
```

### Adding a New Endpoint

1. Create controller in `app/controllers/`
2. Create schema in `app/schemas/` (if needed)
3. Add route to FastAPI app in `main.py`
4. Write unit tests in `tests/unit/`
5. Write integration tests in `tests/integration/`

## Next Steps (Phase 2 Week 5)

**Days 1-2**: ✅ Project Setup
**Days 3-4**: Core Services (email, SMS, templates)
**Day 5**: Event Integration (RabbitMQ, event listener)
**Days 6-7**: Testing & Documentation

## Support

For issues or questions, refer to the main project documentation in the parent directory.
