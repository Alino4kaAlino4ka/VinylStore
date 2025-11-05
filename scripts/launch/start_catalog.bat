@echo off
echo Starting Catalog Service...
cd services\catalog
python -c "from main import app; import uvicorn; print('Starting Catalog Service on port 8000...'); uvicorn.run(app, host='127.0.0.1', port=8000, reload=True)"
