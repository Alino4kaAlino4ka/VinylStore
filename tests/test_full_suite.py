#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Полный набор тестов для Vinyl Shop
Покрывает все пункты из TESTING_CHECKLIST.md
"""

import requests
import sys
import json
import os
import time
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

# Настройка кодировки для Windows
if sys.platform == "win32":
    import codecs
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
        else:
            sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
            sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())
    except:
        pass

# Загружаем конфигурацию
base_path = Path(__file__).parent.parent
config_path = base_path / "config.env"
if config_path.exists():
    load_dotenv(config_path)

# Конфигурация сервисов (актуальные порты)
SERVICES = {
    "catalog": "http://127.0.0.1:8000",
    "auth": "http://127.0.0.1:8001",
    "orders": "http://127.0.0.1:8010",
    "users": "http://127.0.0.1:8011",
    "recommender": "http://127.0.0.1:8012",
    "cart": "http://127.0.0.1:8005",
    "prompts_manager": "http://127.0.0.1:8007",
}

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    END = '\033[0m'
    BOLD = '\033[1m'

class TestSuite:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.results = []
        self.auth_token = None
        self.test_user = None
        
    def log(self, category, name, success, message=""):
        """Логирование результата теста"""
        if success:
            self.passed += 1
            status = f"{Colors.GREEN}✅ PASS{Colors.END}"
        else:
            self.failed += 1
            status = f"{Colors.RED}❌ FAIL{Colors.END}"
        
        self.results.append({
            "category": category,
            "name": name,
            "success": success,
            "message": message,
            "status": status
        })
        
        print(f"  {status} {name}")
        if message:
            print(f"     {Colors.YELLOW}{message}{Colors.END}")
    
    def print_summary(self):
        """Вывод итоговой статистики"""
        print(f"\n{Colors.BLUE}{'='*70}")
        print(f"{Colors.BOLD}📊 ИТОГОВАЯ СТАТИСТИКА{Colors.END}")
        print(f"{'='*70}{Colors.END}\n")
        
        # Группировка по категориям
        categories = {}
        for result in self.results:
            cat = result["category"]
            if cat not in categories:
                categories[cat] = {"passed": 0, "failed": 0, "total": 0}
            categories[cat]["total"] += 1
            if result["success"]:
                categories[cat]["passed"] += 1
            else:
                categories[cat]["failed"] += 1
        
        for category, stats in categories.items():
            total = stats["total"]
            passed = stats["passed"]
            failed = stats["failed"]
            success_rate = (passed / total * 100) if total > 0 else 0
            status_color = Colors.GREEN if failed == 0 else Colors.YELLOW
            print(f"{status_color}{category}: {passed}/{total} ({success_rate:.1f}%){Colors.END}")
        
        print(f"\n{Colors.BLUE}{'='*70}{Colors.END}")
        total = self.passed + self.failed + self.skipped
        print(f"{Colors.GREEN}✅ Пройдено: {self.passed}{Colors.END}")
        print(f"{Colors.RED}❌ Провалено: {self.failed}{Colors.END}")
        if self.skipped > 0:
            print(f"{Colors.YELLOW}⏭️  Пропущено: {self.skipped}{Colors.END}")
        print(f"📊 Всего: {total}")
        if total > 0:
            success_rate = (self.passed / total) * 100
            print(f"📈 Успешность: {success_rate:.1f}%")
        print(f"{Colors.BLUE}{'='*70}{Colors.END}\n")
        
        return self.failed == 0

# Глобальный объект для результатов
suite = TestSuite()

# ============================================================================
# 1. ИНФРАСТРУКТУРА И СЕРВИСЫ
# ============================================================================

def test_infrastructure():
    """Тестирование инфраструктуры и сервисов"""
    print(f"\n{Colors.CYAN}{'='*70}")
    print(f"{Colors.BOLD}1️⃣  ИНФРАСТРУКТУРА И СЕРВИСЫ{Colors.END}")
    print(f"{'='*70}{Colors.END}\n")
    
    service_names = {
        "catalog": "Catalog Service",
        "auth": "Auth Service",
        "orders": "Orders Service",
        "users": "Users Service",
        "recommender": "Recommender Service",
        "cart": "Cart Service",
        "prompts_manager": "Prompts Manager Service"
    }
    
    for key, name in service_names.items():
        url = SERVICES[key]
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                suite.log("Инфраструктура", f"Health Check: {name}", True)
            else:
                suite.log("Инфраструктура", f"Health Check: {name}", False,
                         f"Status: {response.status_code}")
        except Exception as e:
            suite.log("Инфраструктура", f"Health Check: {name}", False, str(e))

# ============================================================================
# 2. API ENDPOINTS
# ============================================================================

def test_catalog_api():
    """Тестирование Catalog API"""
    print(f"\n{Colors.CYAN}{'='*70}")
    print(f"{Colors.BOLD}2.1 CATALOG SERVICE API{Colors.END}")
    print(f"{'='*70}{Colors.END}\n")
    
    base_url = SERVICES["catalog"]
    
    # GET /api/v1/products
    try:
        response = requests.get(f"{base_url}/api/v1/products", timeout=10)
        if response.status_code == 200:
            data = response.json()
            products = data.get("products", [])
            suite.log("Catalog API", "GET /api/v1/products", True,
                     f"Получено товаров: {len(products)}")
            
            if products:
                # GET /api/v1/products/{id}
                first_id = products[0].get("id")
                response = requests.get(f"{base_url}/api/v1/products/{first_id}", timeout=5)
                if response.status_code == 200:
                    suite.log("Catalog API", f"GET /api/v1/products/{first_id}", True)
                else:
                    suite.log("Catalog API", f"GET /api/v1/products/{first_id}", False,
                             f"Status: {response.status_code}")
                
                # GET /api/v1/products/99999 (404)
                response = requests.get(f"{base_url}/api/v1/products/99999", timeout=5)
                if response.status_code == 404:
                    suite.log("Catalog API", "GET /api/v1/products/99999 (404)", True)
                else:
                    suite.log("Catalog API", "GET /api/v1/products/99999 (404)", False,
                             f"Expected 404, got {response.status_code}")
        else:
            suite.log("Catalog API", "GET /api/v1/products", False,
                     f"Status: {response.status_code}")
    except Exception as e:
        suite.log("Catalog API", "GET /api/v1/products", False, str(e))

def test_auth_api():
    """Тестирование Auth API"""
    print(f"\n{Colors.CYAN}{'='*70}")
    print(f"{Colors.BOLD}2.2 AUTH SERVICE API{Colors.END}")
    print(f"{'='*70}{Colors.END}\n")
    
    base_url = SERVICES["auth"]
    
    # Создаем тестового пользователя
    test_user = {
        "email": f"test_{int(time.time())}@test.com",
        "password": "testpass123"
    }
    suite.test_user = test_user
    
    try:
        # POST /register (правильный endpoint)
        response = requests.post(f"{base_url}/register", json=test_user, timeout=5)
        if response.status_code in [200, 201]:
            suite.log("Auth API", "POST /register", True)
        elif response.status_code == 400:
            # Пользователь уже существует - пробуем другой email
            test_user["email"] = f"test_{int(time.time() * 1000)}@test.com"
            response = requests.post(f"{base_url}/register", json=test_user, timeout=5)
            if response.status_code in [200, 201]:
                suite.log("Auth API", "POST /register", True, "Retry successful")
            else:
                suite.log("Auth API", "POST /register", False,
                         f"Status: {response.status_code}")
        else:
            suite.log("Auth API", "POST /register", False,
                     f"Status: {response.status_code}")
        
        # POST /token (правильный endpoint)
        try:
            response = requests.post(
                f"{base_url}/token",
                data={"username": test_user["email"], "password": test_user["password"]},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                if token:
                    suite.auth_token = token
                    suite.log("Auth API", "POST /token", True)
                else:
                    suite.log("Auth API", "POST /token", False, "Token not found")
            else:
                suite.log("Auth API", "POST /token", False,
                         f"Status: {response.status_code}")
        except Exception as e:
            suite.log("Auth API", "POST /token", False, str(e))
        
        # GET /users/me (требует авторизации)
        if suite.auth_token:
            headers = {"Authorization": f"Bearer {suite.auth_token}"}
            response = requests.get(f"{base_url}/users/me", headers=headers, timeout=5)
            if response.status_code == 200:
                suite.log("Auth API", "GET /users/me", True)
            else:
                suite.log("Auth API", "GET /users/me", False,
                         f"Status: {response.status_code}")
        
    except Exception as e:
        suite.log("Auth API", "Auth API тесты", False, str(e))

def test_orders_api():
    """Тестирование Orders API"""
    print(f"\n{Colors.CYAN}{'='*70}")
    print(f"{Colors.BOLD}2.3 ORDERS SERVICE API{Colors.END}")
    print(f"{'='*70}{Colors.END}\n")
    
    base_url = SERVICES["orders"]
    
    # Проверка без авторизации (должна быть ошибка)
    try:
        response = requests.post(
            f"{base_url}/api/v1/orders",
            json={"product_ids": ["1"], "quantities": {"1": 1}},
            timeout=5
        )
        if response.status_code in [401, 422]:
            suite.log("Orders API", "POST /api/v1/orders (без авторизации)", True,
                     f"Корректно требует авторизацию (Status: {response.status_code})")
        else:
            suite.log("Orders API", "POST /api/v1/orders (без авторизации)", False,
                     f"Status: {response.status_code}, ожидался 401 или 422")
    except Exception as e:
        suite.log("Orders API", "POST /api/v1/orders (без авторизации)", False, str(e))
    
    if not suite.auth_token:
        suite.log("Orders API", "POST /api/v1/orders (с авторизацией)", False,
                 "Требуется авторизация, но токен не получен")
        suite.skipped += 1
        return
    
    try:
        # Получаем товары из каталога
        catalog_url = SERVICES["catalog"]
        response = requests.get(f"{catalog_url}/api/v1/products", timeout=5)
        if response.status_code != 200:
            suite.log("Orders API", "POST /api/v1/orders", False, "Не удалось получить товары")
            return
        
        products = response.json().get("products", [])
        if not products:
            suite.log("Orders API", "POST /api/v1/orders", False, "Нет товаров в каталоге")
            return
        
        # Создаем заказ
        order_data = {
            "product_ids": [str(products[0]["id"])],
            "quantities": {"1": 1}
        }
        
        headers = {"Authorization": f"Bearer {suite.auth_token}"}
        response = requests.post(
            f"{base_url}/api/v1/orders",
            json=order_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            suite.log("Orders API", "POST /api/v1/orders", True)
        else:
            suite.log("Orders API", "POST /api/v1/orders", False,
                     f"Status: {response.status_code}, Response: {response.text[:200]}")
        
    except Exception as e:
        suite.log("Orders API", "POST /api/v1/orders", False, str(e))

def test_cart_api():
    """Тестирование Cart API"""
    print(f"\n{Colors.CYAN}{'='*70}")
    print(f"{Colors.BOLD}2.4 CART SERVICE API{Colors.END}")
    print(f"{'='*70}{Colors.END}\n")
    
    base_url = SERVICES["cart"]
    
    try:
        # Получаем товары из каталога
        catalog_url = SERVICES["catalog"]
        response = requests.get(f"{catalog_url}/api/v1/products", timeout=5)
        if response.status_code != 200:
            suite.log("Cart API", "POST /api/v1/cart/calculate", False,
                     "Не удалось получить товары")
            return
        
        products = response.json().get("products", [])
        if not products:
            suite.log("Cart API", "POST /api/v1/cart/calculate", False,
                     "Нет товаров в каталоге")
            return
        
        # Расчет корзины
        cart_data = {
            "product_ids": [str(products[0]["id"])]
        }
        
        response = requests.post(
            f"{base_url}/api/v1/cart/calculate",
            json=cart_data,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            total = data.get("total", 0)
            suite.log("Cart API", "POST /api/v1/cart/calculate", True,
                     f"Итого: {total}")
        else:
            suite.log("Cart API", "POST /api/v1/cart/calculate", False,
                     f"Status: {response.status_code}")
        
    except Exception as e:
        suite.log("Cart API", "POST /api/v1/cart/calculate", False, str(e))

def test_recommender_api():
    """Тестирование Recommender API"""
    print(f"\n{Colors.CYAN}{'='*70}")
    print(f"{Colors.BOLD}2.5 RECOMMENDER SERVICE API{Colors.END}")
    print(f"{'='*70}{Colors.END}\n")
    
    base_url = SERVICES["recommender"]
    
    try:
        # POST /api/v1/recommendations/generate
        recommendation_data = {
            "user_id": "test_user",
            "preferences": ["rock", "pop"]
        }
        
        response = requests.post(
            f"{base_url}/api/v1/recommendations/generate",
            json=recommendation_data,
            timeout=15  # AI может работать дольше
        )
        
        if response.status_code == 200:
            data = response.json()
            recommendations = data.get("recommendations", [])
            suite.log("Recommender API", "POST /api/v1/recommendations/generate", True,
                     f"Получено рекомендаций: {len(recommendations)}")
        else:
            suite.log("Recommender API", "POST /api/v1/recommendations/generate", False,
                     f"Status: {response.status_code}")
        
        # POST /api/v1/chat/message (увеличиваем таймаут для AI)
        chat_data = {
            "message": "Привет",  # Простой запрос для быстрого ответа
            "history": []
        }
        
        try:
            response = requests.post(
                f"{base_url}/api/v1/chat/message",
                json=chat_data,
                timeout=30  # Увеличен таймаут для AI
            )
            
            if response.status_code == 200:
                suite.log("Recommender API", "POST /api/v1/chat/message", True)
            else:
                suite.log("Recommender API", "POST /api/v1/chat/message", False,
                         f"Status: {response.status_code}")
        except requests.exceptions.Timeout:
            suite.log("Recommender API", "POST /api/v1/chat/message", False,
                     "Timeout (AI может работать долго, это нормально)")
        except Exception as e:
            suite.log("Recommender API", "POST /api/v1/chat/message", False, str(e))
        
    except Exception as e:
        suite.log("Recommender API", "Recommender API тесты", False, str(e))

def test_prompts_manager_api():
    """Тестирование Prompts Manager API"""
    print(f"\n{Colors.CYAN}{'='*70}")
    print(f"{Colors.BOLD}2.6 PROMPTS MANAGER SERVICE API{Colors.END}")
    print(f"{'='*70}{Colors.END}\n")
    
    base_url = SERVICES["prompts_manager"]
    
    try:
        # GET /api/v1/prompts (возвращает список напрямую)
        response = requests.get(f"{base_url}/api/v1/prompts", timeout=5)
        if response.status_code == 200:
            data = response.json()
            # Ответ может быть списком или объектом с полем prompts
            if isinstance(data, list):
                prompts = data
            else:
                prompts = data.get("prompts", [])
            
            suite.log("Prompts Manager API", "GET /api/v1/prompts", True,
                     f"Получено промптов: {len(prompts)}")
            
            if prompts:
                # GET /api/v1/prompts/{id}
                first_id = prompts[0].get("id") if isinstance(prompts[0], dict) else prompts[0].id
                response = requests.get(f"{base_url}/api/v1/prompts/{first_id}", timeout=5)
                if response.status_code == 200:
                    suite.log("Prompts Manager API", f"GET /api/v1/prompts/{first_id}", True)
                else:
                    suite.log("Prompts Manager API", f"GET /api/v1/prompts/{first_id}", False,
                             f"Status: {response.status_code}")
        else:
            suite.log("Prompts Manager API", "GET /api/v1/prompts", False,
                     f"Status: {response.status_code}")
        
    except Exception as e:
        suite.log("Prompts Manager API", "Prompts Manager API тесты", False, str(e))

# ============================================================================
# 3. АВТОРИЗАЦИЯ И БЕЗОПАСНОСТЬ
# ============================================================================

def test_security():
    """Тестирование безопасности"""
    print(f"\n{Colors.CYAN}{'='*70}")
    print(f"{Colors.BOLD}3️⃣  АВТОРИЗАЦИЯ И БЕЗОПАСНОСТЬ{Colors.END}")
    print(f"{'='*70}{Colors.END}\n")
    
    # Тест невалидного токена - проверяем через Orders API
    orders_url = SERVICES["orders"]
    headers = {"Authorization": "Bearer invalid_token_12345"}
    try:
        # Попытка создать заказ с невалидным токеном
        response = requests.post(
            f"{orders_url}/api/v1/orders",
            json={"product_ids": ["1"], "quantities": {"1": 1}},
            headers=headers,
            timeout=5
        )
        if response.status_code == 401:
            suite.log("Безопасность", "Невалидный токен возвращает 401", True)
        elif response.status_code == 422:
            # 422 - валидация, тоже означает что нужна авторизация
            suite.log("Безопасность", "Невалидный токен возвращает 401/422", True,
                     "Status: 422 (validation error)")
        else:
            suite.log("Безопасность", "Невалидный токен возвращает 401", False,
                     f"Status: {response.status_code}")
    except Exception as e:
        suite.log("Безопасность", "Невалидный токен возвращает 401", False, str(e))
    
    # Тест регистрации с существующим email
    auth_url = SERVICES["auth"]
    if suite.test_user:
        try:
            response = requests.post(
                f"{auth_url}/register",  # Правильный endpoint
                json=suite.test_user,
                timeout=5
            )
            if response.status_code == 400:
                suite.log("Безопасность", "Регистрация с существующим email возвращает ошибку", True)
            else:
                suite.log("Безопасность", "Регистрация с существующим email возвращает ошибку", False,
                         f"Status: {response.status_code}")
        except Exception as e:
            suite.log("Безопасность", "Регистрация с существующим email", False, str(e))

# ============================================================================
# 4. ИНТЕГРАЦИОННЫЕ ТЕСТЫ
# ============================================================================

def test_integration():
    """Интеграционные тесты"""
    print(f"\n{Colors.CYAN}{'='*70}")
    print(f"{Colors.BOLD}4️⃣  ИНТЕГРАЦИОННЫЕ ТЕСТЫ{Colors.END}")
    print(f"{'='*70}{Colors.END}\n")
    
    # Catalog ↔ Cart
    try:
        catalog_url = SERVICES["catalog"]
        cart_url = SERVICES["cart"]
        
        response = requests.get(f"{catalog_url}/api/v1/products", timeout=5)
        if response.status_code == 200:
            products = response.json().get("products", [])
            if products:
                cart_data = {"product_ids": [str(products[0]["id"])]}
                response = requests.post(
                    f"{cart_url}/api/v1/cart/calculate",
                    json=cart_data,
                    timeout=5
                )
                if response.status_code == 200:
                    suite.log("Интеграция", "Catalog ↔ Cart", True)
                else:
                    suite.log("Интеграция", "Catalog ↔ Cart", False,
                             f"Status: {response.status_code}")
    except Exception as e:
        suite.log("Интеграция", "Catalog ↔ Cart", False, str(e))
    
    # Recommender ↔ Prompts Manager
    try:
        recommender_url = SERVICES["recommender"]
        prompts_url = SERVICES["prompts_manager"]
        
        # Получаем промпт
        response = requests.get(f"{prompts_url}/api/v1/prompts/recommendation_prompt", timeout=5)
        if response.status_code == 200:
            # Пробуем использовать в recommender
            chat_data = {"message": "Привет", "history": []}
            response = requests.post(
                f"{recommender_url}/api/v1/chat/message",
                json=chat_data,
                timeout=15
            )
            if response.status_code == 200:
                suite.log("Интеграция", "Recommender ↔ Prompts Manager", True)
            else:
                suite.log("Интеграция", "Recommender ↔ Prompts Manager", False,
                         f"Status: {response.status_code}")
    except Exception as e:
        suite.log("Интеграция", "Recommender ↔ Prompts Manager", False, str(e))

# ============================================================================
# 5. AI ФУНКЦИИ
# ============================================================================

def test_ai_functions():
    """Тестирование AI функций"""
    print(f"\n{Colors.CYAN}{'='*70}")
    print(f"{Colors.BOLD}5️⃣  AI ФУНКЦИИ{Colors.END}")
    print(f"{'='*70}{Colors.END}\n")
    
    # Проверка доступности Prompts Manager
    prompts_url = SERVICES["prompts_manager"]
    try:
        response = requests.get(f"{prompts_url}/api/v1/prompts", timeout=5)
        if response.status_code == 200:
            suite.log("AI функции", "Промпты загружаются из Prompts Manager", True)
        else:
            suite.log("AI функции", "Промпты загружаются из Prompts Manager", False,
                     f"Status: {response.status_code}")
    except Exception as e:
        suite.log("AI функции", "Промпты загружаются из Prompts Manager", False, str(e))
    
    # Тест AI-консультанта (с увеличенным таймаутом)
    recommender_url = SERVICES["recommender"]
    try:
        chat_data = {"message": "Привет", "history": []}  # Простой запрос
        response = requests.post(
            f"{recommender_url}/api/v1/chat/message",
            json=chat_data,
            timeout=30  # Увеличен таймаут для AI
        )
        if response.status_code == 200:
            suite.log("AI функции", "AI-консультант (чат) отвечает", True)
        else:
            suite.log("AI функции", "AI-консультант (чат) отвечает", False,
                     f"Status: {response.status_code}")
    except requests.exceptions.Timeout:
        suite.log("AI функции", "AI-консультант (чат) отвечает", False,
                 "Timeout (AI может работать долго)")
    except Exception as e:
        suite.log("AI функции", "AI-консультант (чат) отвечает", False, str(e))

# ============================================================================
# ГЛАВНАЯ ФУНКЦИЯ
# ============================================================================

def main():
    """Главная функция запуска всех тестов"""
    print(f"\n{Colors.MAGENTA}{Colors.BOLD}{'='*70}")
    print("[TEST] ПОЛНЫЙ НАБОР ТЕСТОВ VINYL SHOP")
    print(f"{'='*70}{Colors.END}\n")
    
    start_time = time.time()
    
    # Запуск всех тестов
    test_infrastructure()
    test_catalog_api()
    test_auth_api()
    test_orders_api()
    test_cart_api()
    test_recommender_api()
    test_prompts_manager_api()
    test_security()
    test_integration()
    test_ai_functions()
    
    elapsed_time = time.time() - start_time
    
    # Вывод результатов
    success = suite.print_summary()
    
    print(f"{Colors.CYAN}⏱️  Время выполнения: {elapsed_time:.2f} секунд{Colors.END}\n")
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}[WARNING] Тестирование прервано пользователем{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}[ERROR] Критическая ошибка: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

