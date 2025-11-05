// Простые тесты для проверки функций корзины
// Запустите этот код в консоли браузера на странице с подключенным script.js

console.log('🧪 Запуск простых тестов функций корзины...');

// Тест 1: Проверка наличия функций
console.log('\n📋 Проверка наличия функций:');
const functions = ['getCart', 'saveCart', 'addToCart', 'updateCartCount'];
let allFunctionsFound = true;

functions.forEach(func => {
    if (typeof window[func] === 'function') {
        console.log(`✅ ${func}() - найдена`);
    } else {
        console.log(`❌ ${func}() - НЕ найдена`);
        allFunctionsFound = false;
    }
});

if (!allFunctionsFound) {
    console.log('\n⚠️ Некоторые функции не найдены! Проверьте подключение script.js');
    console.log('Убедитесь, что на странице есть: <script src="src/scripts/script.js"></script>');
} else {
    console.log('\n🎉 Все функции найдены! Продолжаем тестирование...');
}

// Тест 2: getCart() с пустой корзиной
console.log('\n🧪 Тест getCart() с пустой корзиной:');
try {
    localStorage.removeItem('cart');
    const emptyCart = getCart();
    if (Array.isArray(emptyCart) && emptyCart.length === 0) {
        console.log('✅ getCart() возвращает пустой массив');
    } else {
        console.log(`❌ getCart() вернул: ${JSON.stringify(emptyCart)}`);
    }
} catch (error) {
    console.log(`❌ Ошибка в getCart(): ${error.message}`);
}

// Тест 3: saveCart() и getCart()
console.log('\n🧪 Тест saveCart() и getCart():');
try {
    const testCart = ['item1', 'item2', 'item3'];
    saveCart(testCart);
    const retrievedCart = getCart();
    if (JSON.stringify(testCart) === JSON.stringify(retrievedCart)) {
        console.log('✅ saveCart() и getCart() работают корректно');
    } else {
        console.log(`❌ Данные не совпадают. Сохранено: ${JSON.stringify(testCart)}, получено: ${JSON.stringify(retrievedCart)}`);
    }
} catch (error) {
    console.log(`❌ Ошибка в saveCart()/getCart(): ${error.message}`);
}

// Тест 4: addToCart()
console.log('\n🧪 Тест addToCart():');
try {
    localStorage.removeItem('cart');
    
    addToCart('test-product-1');
    const cart = getCart();
    if (cart.includes('test-product-1') && cart.length === 1) {
        console.log('✅ addToCart() добавляет товар');
    } else {
        console.log(`❌ addToCart() добавил товар некорректно. Корзина: ${JSON.stringify(cart)}`);
    }
    
    // Тест дубликатов
    addToCart('test-product-1');
    const cartAfterDuplicate = getCart();
    if (cartAfterDuplicate.length === 1) {
        console.log('✅ addToCart() не добавляет дубликаты');
    } else {
        console.log(`❌ addToCart() добавил дубликат. Корзина: ${JSON.stringify(cartAfterDuplicate)}`);
    }
} catch (error) {
    console.log(`❌ Ошибка в addToCart(): ${error.message}`);
}

// Тест 5: updateCartCount()
console.log('\n🧪 Тест updateCartCount():');
try {
    // Создаем элемент счетчика если его нет
    if (!document.getElementById('cart-count')) {
        const countElement = document.createElement('span');
        countElement.id = 'cart-count';
        countElement.textContent = '0';
        document.body.appendChild(countElement);
        console.log('ℹ️ Создан элемент счетчика корзины');
    }
    
    addToCart('count-test-1');
    addToCart('count-test-2');
    updateCartCount();
    
    const countElement = document.getElementById('cart-count');
    if (countElement && countElement.textContent === '2') {
        console.log('✅ updateCartCount() обновляет счетчик');
    } else {
        console.log(`❌ updateCartCount() обновил счетчик на: ${countElement ? countElement.textContent : 'элемент не найден'}`);
    }
} catch (error) {
    console.log(`❌ Ошибка в updateCartCount(): ${error.message}`);
}

// Тест 6: Проверка localStorage
console.log('\n🧪 Тест localStorage:');
try {
    const testData = ['localStorage-test'];
    localStorage.setItem('cart', JSON.stringify(testData));
    const stored = localStorage.getItem('cart');
    if (stored === JSON.stringify(testData)) {
        console.log('✅ localStorage работает корректно');
    } else {
        console.log(`❌ localStorage не работает. Сохранено: ${stored}, ожидалось: ${JSON.stringify(testData)}`);
    }
} catch (error) {
    console.log(`❌ Ошибка в localStorage: ${error.message}`);
}

// Тест 7: Проверка обработчика событий
console.log('\n🧪 Тест обработчика событий:');
try {
    // Создаем тестовую кнопку
    const testButton = document.createElement('button');
    testButton.className = 'add-to-cart-btn';
    testButton.setAttribute('data-product-id', 'event-test');
    testButton.textContent = 'Тестовая кнопка';
    document.body.appendChild(testButton);
    
    // Симулируем клик
    testButton.click();
    
    const cart = getCart();
    if (cart.includes('event-test')) {
        console.log('✅ Обработчик событий работает');
    } else {
        console.log(`❌ Обработчик событий не сработал. Корзина: ${JSON.stringify(cart)}`);
    }
    
    // Удаляем тестовую кнопку
    testButton.remove();
} catch (error) {
    console.log(`❌ Ошибка в обработчике событий: ${error.message}`);
}

console.log('\n🎉 Тестирование завершено!');
console.log('\n📊 Для детального тестирования откройте:');
console.log('- debug_cart.html - для интерактивной отладки');
console.log('- test_cart_frontend.html - для полного набора тестов');
console.log('- test_cart_unit.html - для unit-тестов в консоли');
