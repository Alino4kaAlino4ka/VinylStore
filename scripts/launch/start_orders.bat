@echo off
echo Starting Orders Service...
cd /d "%~dp0services\orders"
python -c "from main import app; import uvicorn; uvicorn.run(app, host='127.0.0.1', port=8002, reload=True)"
pause
