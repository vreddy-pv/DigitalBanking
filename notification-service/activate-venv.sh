#!/bin/bash

# Bash activation script for notification-service virtual environment

echo "Activating notification-service virtual environment..."

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate the virtual environment
source "$SCRIPT_DIR/venv/bin/activate"

echo ""
echo "✓ Virtual environment activated"
echo ""
python --version
pip --version
echo ""
echo "Available commands:"
echo "  uvicorn    - Run ASGI server"
echo "  pytest     - Run tests"
echo "  alembic    - Database migrations"
echo "  python     - Python interpreter"
echo ""
echo "To deactivate: deactivate"
