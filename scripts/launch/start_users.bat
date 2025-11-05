@echo off
echo Starting Users Service...
cd /d "%~dp0services\users"
python -c "from main import app; import uvicorn; uvicorn.run(app, host='127.0.0.1', port=8004, reload=True)"
pause




