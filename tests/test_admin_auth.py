"""
Тесты для системы авторизации администраторов
"""

import unittest
import sys
import os

# Добавляем путь к модулю admin_config
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from admin_config import (
    ADMIN_CREDENTIALS,
    verify_admin_credentials,
    generate_admin_token,
    verify_admin_token
)


class TestAdminConfig(unittest.TestCase):
    """Тесты для конфигурации администратора"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        self.valid_username = "admin"
        self.valid_password = "admin123"
        self.invalid_username = "user"
        self.invalid_password = "wrong_password"
    
    def test_admin_credentials_structure(self):
        """Тест структуры учетных данных администратора"""
        self.assertIsInstance(ADMIN_CREDENTIALS, dict)
        self.assertIn("username", ADMIN_CREDENTIALS)
        self.assertIn("password", ADMIN_CREDENTIALS)
        self.assertEqual(ADMIN_CREDENTIALS["username"], "admin")
        self.assertEqual(ADMIN_CREDENTIALS["password"], "admin123")
    
    def test_verify_admin_credentials_valid(self):
        """Тест проверки валидных учетных данных"""
        result = verify_admin_credentials(self.valid_username, self.valid_password)
        self.assertTrue(result)
    
    def test_verify_admin_credentials_invalid_username(self):
        """Тест проверки невалидного имени пользователя"""
        result = verify_admin_credentials(self.invalid_username, self.valid_password)
        self.assertFalse(result)
    
    def test_verify_admin_credentials_invalid_password(self):
        """Тест проверки невалидного пароля"""
        result = verify_admin_credentials(self.valid_username, self.invalid_password)
        self.assertFalse(result)
    
    def test_verify_admin_credentials_both_invalid(self):
        """Тест проверки невалидных учетных данных"""
        result = verify_admin_credentials(self.invalid_username, self.invalid_password)
        self.assertFalse(result)
    
    def test_verify_admin_credentials_empty_strings(self):
        """Тест проверки пустых строк"""
        result = verify_admin_credentials("", "")
        self.assertFalse(result)
    
    def test_verify_admin_credentials_none_values(self):
        """Тест проверки None значений"""
        result = verify_admin_credentials(None, None)
        self.assertFalse(result)
    
    def test_verify_admin_credentials_case_sensitive(self):
        """Тест чувствительности к регистру"""
        result = verify_admin_credentials("Admin", self.valid_password)
        self.assertFalse(result)
        
        result = verify_admin_credentials(self.valid_username, "Admin123")
        self.assertFalse(result)
    
    def test_generate_admin_token_structure(self):
        """Тест структуры генерируемого токена"""
        token = generate_admin_token()
        self.assertIsInstance(token, str)
        self.assertEqual(len(token), 64)  # SHA256 hash length
        self.assertTrue(token.isalnum())
    
    def test_generate_admin_token_uniqueness(self):
        """Тест уникальности генерируемых токенов"""
        token1 = generate_admin_token()
        token2 = generate_admin_token()
        self.assertNotEqual(token1, token2)
    
    def test_generate_admin_token_multiple_calls(self):
        """Тест множественных вызовов генерации токена"""
        tokens = [generate_admin_token() for _ in range(10)]
        # Все токены должны быть уникальными
        self.assertEqual(len(set(tokens)), 10)
    
    def test_verify_admin_token_valid(self):
        """Тест проверки валидного токена"""
        token = generate_admin_token()
        result = verify_admin_token(token)
        self.assertTrue(result)
    
    def test_verify_admin_token_invalid_format(self):
        """Тест проверки невалидного формата токена"""
        invalid_tokens = [
            "",  # пустая строка
            "short",  # слишком короткий
            "a" * 100,  # слишком длинный
            "invalid-token-with-dashes",  # содержит дефисы
            "invalid_token_with_underscores",  # содержит подчеркивания
            "1234567890",  # только цифры
            "abcdefghijklmnopqrstuvwxyz",  # только буквы
            None  # None значение
        ]
        
        for invalid_token in invalid_tokens:
            result = verify_admin_token(invalid_token)
            self.assertFalse(result, f"Токен '{invalid_token}' должен быть невалидным")
    
    def test_verify_admin_token_edge_cases(self):
        """Тест граничных случаев проверки токена"""
        # Токен правильной длины, но неправильного формата
        edge_case_token = "a" * 64
        result = verify_admin_token(edge_case_token)
        self.assertTrue(result)  # Должен пройти проверку длины и формата
    
    def test_token_generation_and_verification_cycle(self):
        """Тест полного цикла генерации и проверки токена"""
        # Генерируем токен
        token = generate_admin_token()
        
        # Проверяем, что он валиден
        self.assertTrue(verify_admin_token(token))
        
        # Проверяем, что он имеет правильную структуру
        self.assertEqual(len(token), 64)
        self.assertTrue(token.isalnum())


class TestAdminConfigIntegration(unittest.TestCase):
    """Интеграционные тесты для системы авторизации"""
    
    def test_full_authentication_flow(self):
        """Тест полного потока аутентификации"""
        # 1. Проверяем учетные данные
        self.assertTrue(verify_admin_credentials("admin", "admin123"))
        
        # 2. Генерируем токен
        token = generate_admin_token()
        self.assertIsNotNone(token)
        
        # 3. Проверяем токен
        self.assertTrue(verify_admin_token(token))
    
    def test_security_scenarios(self):
        """Тест сценариев безопасности"""
        # Попытка подбора пароля
        common_passwords = ["password", "123456", "admin", "root", "test"]
        for password in common_passwords:
            result = verify_admin_credentials("admin", password)
            self.assertFalse(result, f"Пароль '{password}' не должен быть валидным")
        
        # Попытка подбора имени пользователя
        common_usernames = ["administrator", "root", "user", "test", "guest"]
        for username in common_usernames:
            result = verify_admin_credentials(username, "admin123")
            self.assertFalse(result, f"Имя пользователя '{username}' не должно быть валидным")


def run_tests():
    """Запуск всех тестов"""
    # Создаем тестовый набор
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Добавляем тесты
    suite.addTests(loader.loadTestsFromTestCase(TestAdminConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestAdminConfigIntegration))
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == "__main__":
    print("🧪 Запуск тестов системы авторизации администраторов")
    print("=" * 60)
    
    result = run_tests()
    
    print("\n" + "=" * 60)
    print("📊 Результаты тестирования:")
    print(f"✅ Пройдено: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Провалено: {len(result.failures)}")
    print(f"💥 Ошибок: {len(result.errors)}")
    print(f"📊 Всего: {result.testsRun}")
    
    if result.failures:
        print("\n❌ Проваленные тесты:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n💥 Ошибки:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100
    print(f"📈 Успешность: {success_rate:.1f}%")
    
    if result.wasSuccessful():
        print("\n🎉 Все тесты прошли успешно!")
    else:
        print("\n⚠️ Некоторые тесты провалились. Проверьте реализацию.")
