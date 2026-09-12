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

rem --- 2. Backend dependencies (lock-first, same as CI) -------------------------
echo [2/5] Installing backend dependencies...
if exist "%ROOT%backend\requirements.lock" (
    "%PY%" -m pip install --quiet --disable-pip-version-check -r "%ROOT%backend\requirements.lock"
) else (
    "%PY%" -m pip install --quiet --disable-pip-version-check -r "%ROOT%backend\requirements.txt"
)
if errorlevel 1 (
    echo ERROR: failed to install backend dependencies.
    goto :fail
)

rem --- 3. Frontend dependencies (lock-first, same as CI) -----------------------
echo [3/5] Checking frontend dependencies...
where node >nul 2>nul
if errorlevel 1 (
    echo ERROR: Node.js not found.
    echo Install Node.js 22 or newer ^(LTS^) and run this file again.
    goto :fail
)
rem Version is checked, not just presence: README, CI and the Linux launcher all
rem require Node.js 22+, and this file used to accept any version while its own
rem message said "18 or newer".
for /f "delims=." %%v in ('node -p "process.versions.node"') do set "NODE_MAJOR=%%v"
if %NODE_MAJOR% LSS 22 (
    echo ERROR: Node.js %NODE_MAJOR% found; Node.js 22 or newer is required.
    goto :fail
)
rem A folder named node_modules is NOT proof of a working toolchain: an
rem interrupted install leaves the folder behind with packages missing.
rem The reverse is also true and matters more: re-running `npm ci` over an
rem existing tree performs a bulk delete, and if the environment blocks that
rem delete the tree ends up half removed while the folder still exists. So the
rem toolchain is checked by a real build tool, and installation runs only when
rem it is actually missing.
if exist "%ROOT%frontend\node_modules\.bin\vite.cmd" (
    echo [3/5] Frontend dependencies already installed, skipping npm ci.
) else (
    pushd "%ROOT%frontend"
    if exist "package-lock.json" (
        call npm ci
    ) else (
        call npm install
    )
    popd
    if not exist "%ROOT%frontend\node_modules\.bin\vite.cmd" (
        echo ERROR: frontend toolchain is incomplete ^(node_modules\.bin\vite.cmd missing^).
        echo Delete the frontend\node_modules folder and run this file again.
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
echo Checking that 127.0.0.1:8000 serves our backend and localhost:5173 serves our frontend...
"%PY%" "%ROOT%backend\wait_for_services.py"
if errorlevel 1 (
    echo ERROR: services did not become ready or ports serve foreign processes.
    echo Check the two opened console windows for errors. Browser was NOT opened.
    goto :fail
)

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
