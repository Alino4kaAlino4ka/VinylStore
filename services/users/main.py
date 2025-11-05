from fastapi import FastAPI

# --- Приложение FastAPI ---
app = FastAPI(
    title="Users API",
    description="Микросервис для управления пользователями.",
    version="1.0.0"
)

@app.get("/health", tags=["Health Check"])
def health_check():
    return {"status": "ok"}

@app.get("/api/v1/users", tags=["Users"])
def get_users():
    """Получает список всех пользователей."""
    return {"users": []}

@app.post("/api/v1/users", tags=["Users"])
def create_user():
    """Создает нового пользователя."""
    return {"message": "User created successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8011)  # Изменено на 8011 согласно config.env