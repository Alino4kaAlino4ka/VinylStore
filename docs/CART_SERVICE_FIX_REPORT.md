# Исправление проблемы с Cart Service

## Проблема
Cart Service возвращал не все товары из корзины. В логах было видно:
- В корзине: {3: 1, 5: 1, 21: 1}
- Cart Service вернул: {items: Array(2), total: 578}
- Товар с ID "21" не был найден

## Причина
В Cart Service в моковых данных `MOCK_PRODUCTS` отсутствовали товары с ID 15-22, которые есть в каталоге.

## Исправления

### 1. Добавлены недостающие товары в Cart Service
Добавлены товары с ID 15-22 в `services/cart/main.py`:
```python
"15": CartItem(id="15", title="Дюна", author="ФРЭНК ГЕРБЕРТ", price=34.99, ...),
"16": CartItem(id="16", title="Властелин колец", author="ДЖ.Р.Р. ТОЛКИН", price=39.99, ...),
# ... и так далее до ID 22
```

### 2. Добавлено логирование в Cart Service
```python
print(f"Cart Service: получен запрос с ID товаров: {request.product_ids}")
print(f"Cart Service: найдено товаров: {len(found_ids)}, не найдено: {len(missing_ids)}")
```

### 3. Улучшена обработка ошибок в cart.js
```javascript
// Проверяем, все ли товары найдены
const foundItemIds = data.items.map(item => item.id);
const missingItemIds = productIds.filter(id => !foundItemIds.includes(id));

if (missingItemIds.length > 0) {
    console.warn('Некоторые товары не найдены в Cart Service:', missingItemIds);
    showError(`Внимание: ${missingItemIds.length} товар(ов) временно недоступен(ы) и не включен(ы) в расчет.`);
}
```

### 4. Обновлены моковые данные в cart.js
Добавлены те же товары в fallback данные для случая недоступности Cart Service.

## Результат
- Все товары из каталога теперь доступны в Cart Service
- Добавлено информативное логирование
- Пользователь получает предупреждение о недоступных товарах
- Fallback режим работает корректно

## Тестирование
Обновлен тестовый файл `test_cart_fix.html` с дополнительными тестами:
- Тест Cart Service
- Тест отсутствующих товаров
- Проверка корректного отображения всех товаров

