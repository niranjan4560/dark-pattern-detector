@echo off
title Dark Pattern Detector
color 0A
echo.
echo  ================================================
echo   Dark Pattern Detector - Windows Starter
echo  ================================================
echo.

cd /d "%~dp0"

:: Create venv if not exists
if not exist "venv\Scripts\activate.bat" (
    echo [1/4] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Python not found. Install from python.org
        pause
        exit /b 1
    )
)

:: Activate
call venv\Scripts\activate.bat

:: Install if uvicorn missing
python -c "import uvicorn" 2>nul
if errorlevel 1 (
    echo [2/4] Installing dependencies (takes 2-3 minutes first time)...
    pip install --only-binary=:all: fastapi uvicorn sqlalchemy aiosqlite httpx beautifulsoup4 google-generativeai streamlit plotly pandas requests python-dotenv pydantic reportlab python-multipart lxml 2>nul
    pip install --upgrade sqlalchemy 2>nul
    echo Dependencies installed!
)

:: Create .env if missing
if not exist ".env" (
    echo [3/4] Setting up environment...
    copy .env.example .env >nul
    echo.
    echo *** IMPORTANT: Add your Gemini API key ***
    echo Get FREE key at: https://aistudio.google.com/app/apikey
    echo.
    notepad .env
    echo.
    echo Press any key after saving your .env file...
    pause >nul
)

echo [4/4] Starting services...
echo.

:: Start backend
start "Backend - Dark Pattern Detector" cmd /k "cd /d %~dp0 && venv\Scripts\activate && echo Starting FastAPI backend... && uvicorn backend.main:app --reload --port 8000"

:: Wait for backend
timeout /t 4 /nobreak >nul

:: Start frontend
start "Frontend - Dark Pattern Detector" cmd /k "cd /d %~dp0 && venv\Scripts\activate && echo Starting Streamlit frontend... && streamlit run frontend\app.py --server.port 8501"

:: Wait and open browser
timeout /t 5 /nobreak >nul
start http://localhost:8501

echo.
echo  ================================================
echo   Both services are starting up!
echo  ================================================
echo.
echo   Frontend:  http://localhost:8501
echo   Backend:   http://localhost:8000
echo   API Docs:  http://localhost:8000/docs
echo.
echo   Close the two terminal windows to stop.
echo  ================================================
echo.
pause
