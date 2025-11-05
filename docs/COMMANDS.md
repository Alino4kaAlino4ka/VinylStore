# Project Commands

This file documents the common commands used for setting up and running the "audio-store" project.

## 1. Install Dependencies

To install all the necessary Python packages, run the following command from the root directory:

```bash
pip install -r requirements.txt
```

## 2. Initialize the Database

Before running the application for the first time, you need to create the database and all its tables.

```bash
python init_db.py
```
This command will create an `audio_store.db` file in the root directory.

## 3. Run Tests

To ensure that all components are working as expected, you can run the test suite:

```bash
python -m unittest discover -s tests
```

## 4. Run a Microservice

To run one of the FastAPI microservices, use `uvicorn` with the `--reload` flag for development.

### Запуск сервиса "Каталог"
```bash
uvicorn services.catalog.main:app --host 0.0.0.0 --port 8002 --reload
```

### Запуск сервиса "Корзина"
```bash
uvicorn services.cart.main:app --host 0.0.0.0 --port 8003 --reload
```

### Запуск сервиса "Заказы"
```bash
uvicorn services.orders.main:app --host 0.0.0.0 --port 8004 --reload
```
