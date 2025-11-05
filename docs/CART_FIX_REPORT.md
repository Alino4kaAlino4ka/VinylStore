# Исправление проблемы с корзиной

## Проблема
В корзине появлялись записи с ID "[object Object]" вместо корректных ID товаров. Это приводило к тому, что:
- В корзине отображался только один товар вместо нескольких
- Некорректные записи накапливались в localStorage
- Сервис корзины получал неправильные данные

## Причина
Проблема возникала в файле `src/scripts/catalog.js` в строке 364:
```javascript
<button class="buy-btn" onclick="addToCart(${book.id})">В корзину</button>
```

Когда `book.id` являлся объектом (что могло происходить при обработке данных с сервера), он преобразовывался в строку "[object Object]".

## Исправления

### 1. Исправлен вызов addToCart в catalog.js
**Было:**
```javascript
onclick="addToCart(${book.id})"
```

**Стало:**
```javascript
onclick="addToCart('${book.id}')"
```

### 2. Добавлена нормализация ID в функции addToCart
```javascript
function addToCart(bookId) {
    const normalizedId = String(bookId);
    console.log('addToCart вызвана с ID:', bookId, 'нормализованный ID:', normalizedId);
    
    const book = audiobooks.find(b => String(b.id) === normalizedId);
    // ...
}
```

### 3. Добавлена проверка в addToCartWithQuantity
```javascript
function addToCartWithQuantity(productId) {
    const normalizedId = String(productId);
    
    // Проверяем, что ID не является [object Object]
    if (normalizedId === '[object Object]') {
        console.error('Обнаружен некорректный ID [object Object], пропускаем добавление');
        return;
    }
    // ...
}
```

### 4. Добавлена функция очистки некорректных записей
```javascript
function cleanCartData() {
    const cartWithQuantity = getCartWithQuantity();
    const cleanedCart = {};
    
    Object.keys(cartWithQuantity).forEach(key => {
        if (key !== '[object Object]' && key !== 'undefined' && key !== 'null' && key !== '') {
            cleanedCart[key] = cartWithQuantity[key];
        } else {
            console.warn('Удален некорректный ключ из корзины:', key);
        }
    });
    
    if (Object.keys(cleanedCart).length !== Object.keys(cartWithQuantity).length) {
        saveCartWithQuantity(cleanedCart);
    }
}
```

### 5. Улучшена функция миграции данных
Добавлена проверка на некорректные ID при миграции старых данных корзины.

## Результат
- Корректные ID товаров передаются в корзину
- Некорректные записи автоматически очищаются
- Добавлено логирование для отладки
- Корзина корректно отображает все добавленные товары

## Тестирование
Создан тестовый файл `test_cart_fix.html` для проверки исправлений.

