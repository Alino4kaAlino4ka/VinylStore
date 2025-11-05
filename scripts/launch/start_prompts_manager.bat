@echo off
chcp 65001 >nul
echo Starting Prompts Manager Service on port 8007...
echo.

cd /d %~dp0
cd services\prompts-manager
python -c "from main import app; import uvicorn; uvicorn.run(app, host='127.0.0.1', port=8007, reload=True)"

pause

