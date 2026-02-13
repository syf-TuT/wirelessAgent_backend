#!/bin/bash

# WirelessAgent Backend Project Initialization Script
# This script sets up the development environment and runs health checks

set -e

echo "========================================"
echo "WirelessAgent Backend - Init Script"
echo "========================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

if python -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)"; then
    echo "✓ Python version is compatible (>= 3.9)"
else
    echo "✗ Python version must be >= 3.9"
    exit 1
fi
echo ""

# Setup virtual environment if not exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python -m venv .venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source .venv/Scripts/activate
else
    source .venv/bin/activate
fi
echo "✓ Virtual environment activated"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt
pip install -q -r requirements-dev.txt 2>/dev/null || echo "No dev requirements found"
echo "✓ Dependencies installed"
echo ""

# Check directory structure
echo "Checking directory structure..."
dirs=("app" "app/api" "app/core" "app/models" "app/services" "app/utils" "tests" "tests/unit" "tests/integration" "scripts" "docs")
for dir in "${dirs[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        echo "  Created directory: $dir"
    fi
done
echo "✓ Directory structure verified"
echo ""

# Run health check
echo "Running health checks..."
python -c "
import sys
try:
    # Check if we can import key modules
    import fastapi
    import uvicorn
    import pydantic
    import langchain
    import langgraph
    print('  ✓ All key dependencies importable')

    # Check if we can create FastAPI app
    from fastapi import FastAPI
    app = FastAPI()
    print('  ✓ FastAPI app can be created')

    sys.exit(0)
except Exception as e:
    print(f'  ✗ Health check failed: {e}')
    sys.exit(1)
"
echo ""

# Run tests if they exist
if [ -d "tests" ] && [ "$(ls -A tests 2>/dev/null)" ]; then
    echo "Running tests..."
    python -m pytest tests/ -v --tb=short 2>/dev/null || echo "  No tests found or tests failed"
    echo ""
fi

echo "========================================"
echo "Initialization Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "  1. Review feature_list.json for planned features"
echo "  2. Run 'python main.py' to start the backend server"
echo "  3. Run 'python -m pytest tests/' to run tests"
echo ""
