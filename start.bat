@echo off
rem ---------------------------------------------------------------------------
rem One-click launch of the decision support system:
rem   FastAPI backend  -> http://127.0.0.1:8000
rem   React frontend   -> http://localhost:5173
rem ASCII-only file on purpose: Windows console encoding can corrupt Cyrillic.
rem ---------------------------------------------------------------------------
setlocal

set "ROOT=%~dp0"
set "VENV=%ROOT%.venv"
set "PY=%VENV%\Scripts\python.exe"

echo.
echo === Game dev optimization DSS: startup ===
echo.

rem --- 1. Virtual environment -------------------------------------------------
if exist "%PY%" (
    echo [1/5] Virtual environment found.
) else (
    echo [1/5] Creating virtual environment...
    python -m venv "%VENV%" 2>nul
    if errorlevel 1 py -3 -m venv "%VENV%"
    if not exist "%PY%" (
        echo ERROR: cannot create virtual environment.
        echo Install Python 3.11 or newer and run this file again.
        goto :fail
    )
)

rem --- 2. Backend dependencies ------------------------------------------------
echo [2/5] Installing backend dependencies...
"%PY%" -m pip install --quiet --disable-pip-version-check -r "%ROOT%backend\requirements.txt"
if errorlevel 1 (
    echo ERROR: failed to install backend dependencies.
    goto :fail
)

rem --- 3. Frontend dependencies -----------------------------------------------
if exist "%ROOT%frontend\node_modules" (
    echo [3/5] Frontend dependencies found.
) else (
    echo [3/5] Installing frontend dependencies...
    pushd "%ROOT%frontend"
    call npm install
    popd
    if not exist "%ROOT%frontend\node_modules" (
        echo ERROR: failed to install frontend dependencies.
        echo Install Node.js 18 or newer and run this file again.
        goto :fail
    )
)

rem --- 4. Launch services -----------------------------------------------------
echo [4/5] Starting backend...
start "DSS backend" "%ROOT%backend\run.bat"

echo [5/5] Starting frontend...
start "DSS frontend" "%ROOT%frontend\run.bat"

echo.
echo Waiting for the services to come up...
timeout /t 10 /nobreak >nul

start "" http://localhost:5173

echo.
echo   Frontend  http://localhost:5173
echo   Backend   http://127.0.0.1:8000/api/docs
echo.
echo Close the two opened console windows to stop the services.
echo.

endlocal
exit /b 0

:fail
echo.
echo Startup failed. See the message above.
pause
endlocal
exit /b 1
