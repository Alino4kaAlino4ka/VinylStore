import requests
import time

def test_auth_service():
    """Тестирует сервис аутентификации"""
    base_url = "http://localhost:8005"
    
    print("Тестирование сервиса аутентификации...")
    
    # Тест 1: Проверка health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✓ Health check: OK")
            print(f"  Response: {response.json()}")
        else:
            print(f"✗ Health check failed: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("✗ Сервис не отвечает на порту 8005")
        print("  Убедитесь, что сервис аутентификации запущен")
        return False
    except Exception as e:
        print(f"✗ Ошибка при проверке health: {e}")
        return False
    
    # Тест 2: Регистрация нового пользователя
    try:
        test_user = {
            "email": "test@example.com",
            "password": "test123"
        }
        response = requests.post(f"{base_url}/register", json=test_user, timeout=5)
        if response.status_code == 201:
            print("✓ Регистрация: OK")
        elif response.status_code == 400:
            print("✓ Регистрация: Пользователь уже существует (ожидаемо)")
        else:
            print(f"✗ Регистрация failed: {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"✗ Ошибка при регистрации: {e}")
    
    # Тест 3: Вход с существующим пользователем
    try:
        login_data = {
            "username": "Uzer@gmail.com",
            "password": "Uzer"
        }
        response = requests.post(f"{base_url}/token", data=login_data, timeout=5)
        if response.status_code == 200:
            print("✓ Вход: OK")
            token_data = response.json()
            print(f"  Получен токен: {token_data['access_token'][:20]}...")
        else:
            print(f"✗ Вход failed: {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"✗ Ошибка при входе: {e}")
    
    return True

if __name__ == "__main__":
    test_auth_service()
