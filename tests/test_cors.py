import requests

def test_cors():
    """Тестирует CORS настройки"""
    base_url = "http://localhost:8005"
    
    print("Тестирование CORS...")
    
    # Тест 1: OPTIONS запрос на /register
    try:
        headers = {
            'Origin': 'null',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        response = requests.options(f"{base_url}/register", headers=headers, timeout=5)
        print(f"OPTIONS /register: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if 'Access-Control-Allow-Origin' in response.headers:
            print("✓ CORS headers присутствуют")
        else:
            print("✗ CORS headers отсутствуют")
            
    except Exception as e:
        print(f"✗ Ошибка при тестировании OPTIONS: {e}")
    
    # Тест 2: POST запрос на /register
    try:
        headers = {
            'Content-Type': 'application/json',
            'Origin': 'null'
        }
        data = {
            "email": "test@example.com",
            "password": "test123"
        }
        response = requests.post(f"{base_url}/register", json=data, headers=headers, timeout=5)
        print(f"POST /register: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
    except Exception as e:
        print(f"✗ Ошибка при тестировании POST: {e}")

if __name__ == "__main__":
    test_cors()
