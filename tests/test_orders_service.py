import unittest
import httpx
import asyncio

class TestOrdersService(unittest.TestCase):

    ORDERS_SERVICE_URL = "http://localhost:8004"

    async def test_create_order_successfully(self):
        """
        Тестирует успешное создание заказа через эндпоинт.
        """
        # --- Arrange ---
        # Книга "Dune" (ID=1, price=24.99) * 1
        # Книга "1984"  (ID=2, price=19.99) * 2
        payload = {
            "items": [
                {"audiobook_id": 1, "quantity": 1},
                {"audiobook_id": 2, "quantity": 2}
            ]
        }
        
        # Ожидаемая цена: 24.99 * 1 + 19.99 * 2 = 64.97
        expected_total_price = 64.97
        
        # --- Act ---
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.ORDERS_SERVICE_URL}/api/v1/orders", 
                json=payload
            )
            
        # --- Assert ---
        self.assertEqual(response.status_code, 201)
        
        response_data = response.json()
        
        # Проверяем ключевые поля в ответе
        self.assertIn("id", response_data)
        self.assertIn("created_at", response_data)
        self.assertEqual(len(response_data["items"]), 2)
        
        # Проверяем итоговую стоимость
        self.assertAlmostEqual(response_data["total_price"], expected_total_price, places=2)

    async def test_create_order_with_partial_valid_items(self):
        """
        Тестирует, что заказ создается только с валидными товарами,
        игнорируя несуществующие.
        """
        # --- Arrange ---
        # Книга "Dune" (ID=1, price=24.99)
        # Несуществующий товар (ID=999)
        payload = {
            "items": [
                {"audiobook_id": 1, "quantity": 2}, # 2 * 24.99 = 49.98
                {"audiobook_id": 999, "quantity": 1}
            ]
        }
        
        expected_total_price = 49.98
        
        # --- Act ---
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.ORDERS_SERVICE_URL}/api/v1/orders", 
                json=payload
            )
            
        # --- Assert ---
        self.assertEqual(response.status_code, 201)
        
        response_data = response.json()
        
        # В заказе должен быть только один товар
        self.assertEqual(len(response_data["items"]), 1)
        self.assertEqual(response_data["items"][0]["audiobook_id"], 1)
        
        # Проверяем итоговую стоимость
        self.assertAlmostEqual(response_data["total_price"], expected_total_price, places=2)

    async def test_create_order_with_empty_cart(self):
        """
        Тестирует, что нельзя создать заказ с пустой или полностью невалидной корзиной.
        """
        # --- Arrange ---
        payload = {
            "items": [
                {"audiobook_id": 999, "quantity": 1}
            ]
        }
        
        # --- Act ---
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.ORDERS_SERVICE_URL}/api/v1/orders", 
                json=payload
            )
            
        # --- Assert ---
        # Сервис должен вернуть ошибку, так как после валидации корзина пуста
        self.assertEqual(response.status_code, 400)
        self.assertIn("Корзина пуста или невалидна", response.text)

    # Обертки для запуска асинхронных тестов
    def test_sync_successful_order(self):
        asyncio.run(self.test_create_order_successfully())

    def test_sync_partial_order(self):
        asyncio.run(self.test_create_order_with_partial_valid_items())

    def test_sync_empty_cart_order(self):
        asyncio.run(self.test_create_order_with_empty_cart())

if __name__ == "__main__":
    unittest.main()
