import unittest
import httpx
import asyncio
from sqlalchemy.orm import Session

# Adjusting imports to be relative from the project root
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import connection, models

def clear_users_table():
    """
    Helper function to delete all users from the database before a test run.
    """
    db = connection.SessionLocal()
    try:
        db.query(models.User).delete()
        db.commit()
    finally:
        db.close()

class TestAuthService(unittest.TestCase):

    SERVICE_URL = "http://localhost:8005"
    TEST_USER_EMAIL = "test_user@example.com"
    TEST_USER_PASSWORD = "a_strong_password"

    def setUp(self):
        """
        Clear the users table before each test to ensure isolation.
        """
        clear_users_table()

    async def test_01_register_user_success(self):
        """
        Тест успешной регистрации нового пользователя.
        """
        payload = {"email": self.TEST_USER_EMAIL, "password": self.TEST_USER_PASSWORD}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.SERVICE_URL}/register", json=payload)
            
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["email"], self.TEST_USER_EMAIL)

    async def test_02_register_user_duplicate_email(self):
        """
        Тест ошибки при регистрации пользователя с уже существующим email.
        """
        # Сначала регистрируем пользователя
        payload = {"email": self.TEST_USER_EMAIL, "password": self.TEST_USER_PASSWORD}
        async with httpx.AsyncClient() as client:
            await client.post(f"{self.SERVICE_URL}/register", json=payload)
        
        # Пытаемся зарегистрировать его снова
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.SERVICE_URL}/register", json=payload)
            
        self.assertEqual(response.status_code, 400)

    async def test_03_login_success(self):
        """
        Тест успешного входа и получения JWT-токена.
        """
        # Сначала регистрируем пользователя
        register_payload = {"email": self.TEST_USER_EMAIL, "password": self.TEST_USER_PASSWORD}
        async with httpx.AsyncClient() as client:
            await client.post(f"{self.SERVICE_URL}/register", json=register_payload)

        # Пытаемся войти
        login_data = {"username": self.TEST_USER_EMAIL, "password": self.TEST_USER_PASSWORD}
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.SERVICE_URL}/token", data=login_data)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["token_type"], "bearer")

    async def test_04_login_wrong_password(self):
        """
        Тест ошибки входа с неверным паролем.
        """
        # Регистрируем пользователя
        register_payload = {"email": self.TEST_USER_EMAIL, "password": self.TEST_USER_PASSWORD}
        async with httpx.AsyncClient() as client:
            await client.post(f"{self.SERVICE_URL}/register", json=register_payload)

        # Пытаемся войти с неверным паролем
        login_data = {"username": self.TEST_USER_EMAIL, "password": "wrong_password"}
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.SERVICE_URL}/token", data=login_data)
        
        self.assertEqual(response.status_code, 401)


    # Обертки для запуска асинхронных тестов
    def test_sync_register(self):
        asyncio.run(self.test_01_register_user_success())
        
    def test_sync_register_duplicate(self):
        asyncio.run(self.test_02_register_user_duplicate_email())
        
    def test_sync_login(self):
        asyncio.run(self.test_03_login_success())

    def test_sync_login_fail(self):
        asyncio.run(self.test_04_login_wrong_password())

if __name__ == "__main__":
    unittest.main()
