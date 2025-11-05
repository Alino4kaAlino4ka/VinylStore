@echo off
echo Starting Auth Service...
cd /d "%~dp0services\auth"
python -c "from main import app; import uvicorn; uvicorn.run(app, host='127.0.0.1', port=8005, reload=True)"
pause
