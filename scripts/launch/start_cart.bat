@echo off
echo Starting Cart Service...
cd /d "%~dp0services\cart"
python -c "from main import app; import uvicorn; uvicorn.run(app, host='127.0.0.1', port=8001, reload=True)"
pause
