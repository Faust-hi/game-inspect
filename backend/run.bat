@echo off
rem ---------------------------------------------------------------------------
rem Starts the FastAPI backend on http://127.0.0.1:8000
rem ASCII-only file on purpose: Windows console encoding can corrupt Cyrillic.
rem ---------------------------------------------------------------------------
setlocal

cd /d "%~dp0"

set "VENV=%~dp0..\.venv"
set "PY=%VENV%\Scripts\python.exe"

if not exist "%PY%" (
    echo Virtual environment is missing. Run start.bat from the project root first.
    pause
    exit /b 1
)

echo Backend starting on http://127.0.0.1:8000
"%PY%" -m uvicorn app.main:app --host 127.0.0.1 --port 8000

endlocal
