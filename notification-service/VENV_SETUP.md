# Virtual Environment Setup Guide

## Overview

The Notification Service has its own isolated Python virtual environment located in `notification-service/venv/`. This ensures:

✅ **Project Isolation**: Dependencies don't affect other modules  
✅ **Version Control**: Exact versions specified in requirements.txt  
✅ **Reproducibility**: Same environment across machines  
✅ **Clean Workspace**: No global Python pollution  

---

## Virtual Environment Location

```
C:\Veera\AI\agents\DigitalBanking\
├── notification-service/
│  ├── venv/                       # ← Virtual environment (isolated)
│  │  ├── Scripts/                 # Activation & executable scripts
│  │  ├── Lib/                     # All dependencies installed here
│  │  └── Include/                 # C headers
│  ├── app/
│  ├── tests/
│  ├── requirements.txt
│  └── .gitignore                  # Ignores venv/ directory
│
└── [Other modules unaffected]
```

---

## Installed Packages (34 total)

| Category | Packages | Version |
|----------|----------|---------|
| **Web Framework** | FastAPI, Starlette, Uvicorn | 0.104.1, 0.27.0, 0.24.0 |
| **ORM/Database** | SQLAlchemy, psycopg2-binary | 2.0.23, 2.9.9 |
| **Migrations** | Alembic, Mako | 1.13.1, 1.3.12 |
| **Validation** | Pydantic, pydantic-settings | 2.5.0, 2.1.0 |
| **Email** | aiosmtplib | 3.0.1 |
| **Templates** | Jinja2, MarkupSafe | 3.1.2, 3.0.3 |
| **Message Queue** | pika | 1.3.2 |
| **Configuration** | python-dotenv | 1.0.0 |
| **Testing** | pytest, pytest-asyncio | 7.4.3, 0.23.2 |
| **HTTP Client** | httpx, httpcore | 0.25.2, 1.0.9 |
| **Utilities** | click, anyio, sniffio, idna | Various |

---

## Activation Methods

### Method 1: PowerShell (Windows) - Recommended ⭐

**Quick activation**:
```powershell
cd C:\Veera\AI\agents\DigitalBanking\notification-service
.\venv\Scripts\Activate.ps1
```

**Using activation script**:
```powershell
cd notification-service
.\activate-venv.ps1
```

**After activation**:
```
(venv) PS C:\...\notification-service>
```

**Deactivate**:
```powershell
deactivate
```

---

### Method 2: Command Prompt (Windows)

**Activate**:
```cmd
cd C:\Veera\AI\agents\DigitalBanking\notification-service
venv\Scripts\activate.bat
```

**Deactivate**:
```cmd
deactivate.bat
```

---

### Method 3: Bash/Linux/macOS

**Activate**:
```bash
cd /path/to/notification-service
source venv/bin/activate

# Or using activation script
bash activate-venv.sh
```

**Deactivate**:
```bash
deactivate
```

---

## Verification

### Check Virtual Environment is Active

```powershell
# Should show path to venv/Scripts/python.exe
python -c "import sys; print(sys.executable)"
```

Expected output:
```
C:\Veera\AI\agents\DigitalBanking\notification-service\venv\Scripts\python.exe
```

### List Installed Packages

```powershell
pip list
```

Expected output: 34 packages including fastapi, sqlalchemy, pytest, etc.

### Check Python Version

```powershell
python --version
# Output: Python 3.12.7

pip --version
# Output: pip 24.2 from .../venv/Lib/site-packages/pip (python 3.12)
```

---

## Common Tasks

### Run the Application

```powershell
# Ensure venv is activated
.\activate-venv.ps1

# Start FastAPI development server
uvicorn app.main:app --reload --port 8006
```

### Run Tests

```powershell
# Activate venv
.\activate-venv.ps1

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_notification_service.py -v
```

### Database Migrations

```powershell
# Activate venv
.\activate-venv.ps1

# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1
```

### Install New Package

```powershell
# Activate venv
.\activate-venv.ps1

# Install package
pip install package-name

# Update requirements.txt
pip freeze > requirements.txt
```

---

## Isolation Benefits

### ✅ Project-Specific Dependencies

Each service has its own virtual environment:
- **notification-service**: FastAPI, pika (RabbitMQ), aiosmtplib
- **auth-service**: Spring Boot (Java, no Python)
- **account-service**: Spring Boot (Java, no Python)
- Other services: Isolated from notification-service

### ✅ Version Control

No conflicts between services:
- Notification Service: Python 3.12
- Future services: Can use different Python versions
- Each service's requirements.txt is independent

### ✅ Clean Up

Remove entire environment without affecting other services:
```powershell
# This won't affect other modules
Remove-Item -Recurse venv/
python -m venv venv
pip install -r requirements.txt
```

---

## Git Configuration

The `.gitignore` file ensures the venv directory is NOT committed:

```gitignore
# Virtual Environment
venv/
env/
ENV/
.venv/
```

This means:
- ✅ `requirements.txt` is committed (lists all dependencies)
- ❌ `venv/` is NOT committed (too large, machine-specific)

To recreate on another machine:
```powershell
python -m venv venv
pip install -r requirements.txt
```

---

## Development Workflow

### First Time Setup

```powershell
# 1. Create virtual environment
python -m venv venv

# 2. Activate
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
copy .env.example .env

# 5. Run migrations
alembic upgrade head

# 6. Start development server
uvicorn app.main:app --reload --port 8006
```

### Daily Development

```powershell
# 1. Activate virtual environment
.\activate-venv.ps1

# 2. Make code changes

# 3. Run tests
pytest tests/ -v

# 4. Start server (if needed)
uvicorn app.main:app --reload --port 8006
```

### Adding New Dependency

```powershell
# 1. Activate venv
.\activate-venv.ps1

# 2. Install package
pip install new-package

# 3. Update requirements.txt
pip freeze > requirements.txt

# 4. Commit
git add requirements.txt
git commit -m "[chore] Add new-package dependency"
```

---

## Troubleshooting

### Virtual Environment Not Activating

**Windows PowerShell Issue**: Execution Policy

```powershell
# Check current policy
Get-ExecutionPolicy

# If it's 'Restricted', allow local scripts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Then try activation again**:
```powershell
.\venv\Scripts\Activate.ps1
```

### Package Not Found After Installation

```powershell
# Make sure venv is ACTIVE (shows (venv) in prompt)
pip install -r requirements.txt

# Verify
pip list | grep package-name
```

### Corrupted Virtual Environment

**Full reset**:
```powershell
# 1. Deactivate if active
deactivate

# 2. Remove venv
Remove-Item -Recurse venv/

# 3. Recreate
python -m venv venv

# 4. Activate
.\venv\Scripts\Activate.ps1

# 5. Install
pip install -r requirements.txt
```

---

## Environment Variables

Create `.env` file in notification-service root:

```bash
# Copy from template
copy .env.example .env

# Edit with your settings
DATABASE_URL=postgresql://notification_user:password@localhost:5432/notification_db
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

The application loads these via `python-dotenv` in `config.py`.

---

## Next Steps

✅ Virtual environment created and isolated  
✅ 34 packages installed  
✅ Ready for development  

**Next**:
1. Run migrations: `alembic upgrade head`
2. Start server: `uvicorn app.main:app --reload --port 8006`
3. Test endpoints: `curl http://localhost:8006/health`
4. Begin Days 3-4 development: Core services (email, SMS, templates)

---

**Status**: 🟢 **READY FOR DEVELOPMENT**
