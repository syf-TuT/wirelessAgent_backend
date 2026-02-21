# Project Rules

## Python Environment

All Python commands should be executed using the virtual environment located at `.venv/`.

### Python Command Execution

When running Python commands, always use the virtual environment Python interpreter:

- Use `.venv/Scripts/python.exe` instead of `python` or `python3`
- Use `.venv/Scripts/pip.exe` instead of `pip` or `pip3`

### Examples

**Correct:**
```bash
.venv/Scripts/python.exe backend_server.py
.venv/Scripts/pip.exe install fastapi
```

**Incorrect:**
```bash
python backend_server.py
pip install fastapi
```

### Package Installation

When installing Python packages, always use the virtual environment's pip:

```bash
.venv/Scripts/pip.exe install package_name
```

### Running Scripts

When running Python scripts, always use the virtual environment's Python interpreter:

```bash
.venv/Scripts/python.exe script_name.py
```

### Testing

When running tests, use the virtual environment's Python interpreter:

```bash
.venv/Scripts/python.exe -m pytest
```

### Linting and Type Checking

When running linting or type checking tools, use the virtual environment's Python interpreter:

```bash
.venv/Scripts/python.exe -m black .
.venv/Scripts/python.exe -m mypy .
```
