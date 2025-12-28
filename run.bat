@echo off
echo ========================================
echo   Personal Color Analysis
echo ========================================
echo.
echo Starting the application...
echo.
echo Once started, open your browser to:
echo http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

