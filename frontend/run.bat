@echo off
rem ---------------------------------------------------------------------------
rem Starts the React frontend on http://localhost:5173
rem ASCII-only file on purpose: Windows console encoding can corrupt Cyrillic.
rem ---------------------------------------------------------------------------
setlocal

cd /d "%~dp0"

if not exist "%~dp0node_modules" (
    echo node_modules is missing. Run start.bat from the project root first.
    pause
    exit /b 1
)

echo Frontend starting on http://localhost:5173
call npm run dev

endlocal
