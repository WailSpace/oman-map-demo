@echo off
echo ========================================================
echo  Starting Oman High-Resolution Geospatial Platform Demo
echo ========================================================
cd /d "%~dp0"
call .venv\Scripts\activate.bat
echo Starting FastAPI & Web Dashboard on http://127.0.0.1:8000 ...
python -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload
pause
