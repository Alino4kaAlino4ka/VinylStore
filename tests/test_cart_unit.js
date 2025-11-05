/**
 * Unit тесты для функционала корзины
 * Этот файл содержит детальные тесты для всех функций корзины
 */

class CartTestSuite {
    constructor() {
        this.tests = [];
        this.passed = 0;
        this.failed = 0;
        this.results = [];
    }

    // Добавляет тест в набор
    addTest(name, testFunction) {
        this.tests.push({ name, testFunction });
    }

    // Запускает все тесты
    async runAllTests() {
        console.log('🧪 Запуск тестов функционала корзины...\n');
        
        for (const test of this.tests) {
            try {
                await this.runTest(test);
            } catch (error) {
                this.handleTestFailure(test.name, error);
            }
        }
        
        this.printSummary();
        return this.results;
    }

    // Запускает отдельный тест
    async runTest(test) {
        try {
            const result = await test.testFunction();
            if (result === true || result === undefined) {
                this.handleTestSuccess(test.name);
            } else {
                this.handleTestFailure(test.name, new Error('Тест вернул false'));
            }
        } catch (error) {
            this.handleTestFailure(test.name, error);
        }
    }

    // Обрабатывает успешный тест
    handleTestSuccess(testName) {
        this.passed++;
        this.results.push({ name: testName, status: 'PASSED', error: null });
        console.log(`✅ ${testName}`);
    }

    // Обрабатывает проваленный тест
    handleTestFailure(testName, error) {
        this.failed++;
        this.results.push({ name: testName, status: 'FAILED', error: error.message });
        console.log(`❌ ${testName}: ${error.message}`);
    }

    // Выводит сводку результатов
    printSummary() {
        console.log('\n📊 Сводка результатов:');
        console.log(`✅ Пройдено: ${this.passed}`);
        console.log(`❌ Провалено: ${this.failed}`);
        console.log(`📊 Всего: ${this.passed + this.failed}`);
        console.log(`📈 Успешность: ${((this.passed / (this.passed + this.failed)) * 100).toFixed(1)}%`);
    }

    // Очищает localStorage перед тестом
    clearCart() {
        localStorage.removeItem('cart');
    }

    // Создает мок DOM элементов
    createMockDOM() {
        // Создаем элемент счетчика корзины если его нет
        if (!document.getElementById('cart-count')) {
            const countElement = document.createElement('span');
            countElement.id = 'cart-count';
            countElement.textContent = '0';
            document.body.appendChild(countElement);
        }

        // Создаем тестовые кнопки
        const testContainer = document.createElement('div');
        testContainer.innerHTML = `
            <button class="add-to-cart-btn" data-product-id="test-1">Тест 1</button>
            <button class="add-to-cart-btn" data-product-id="test-2">Тест 2</button>
            <button class="add-to-cart-btn" data-product-id="test-3">Тест 3</button>
        `;
        document.body.appendChild(testContainer);
    }

    // Удаляет мок DOM элементы
    cleanupMockDOM() {
        const countElement = document.getElementById('cart-count');
        if (countElement) {
            countElement.remove();
        }
        
        const testButtons = document.querySelectorAll('.add-to-cart-btn[data-product-id^="test-"]');
        testButtons.forEach(button => {
            button.parentElement.remove();
        });
    }
}

// Создаем экземпляр тестового набора
const testSuite = new CartTestSuite();

// Тесты для localStorage функций
testSuite.addTest('getCart() возвращает пустой массив для новой корзины', () => {
    testSuite.clearCart();
    const cart = getCart();
    return Array.isArray(cart) && cart.length === 0;
});

testSuite.addTest('saveCart() сохраняет корзину в localStorage', () => {
    testSuite.clearCart();
    const testCart = ['item1', 'item2', 'item3'];
    saveCart(testCart);
    const storedCart = localStorage.getItem('cart');
    return storedCart === JSON.stringify(testCart);
});

testSuite.addTest('getCart() возвращает сохраненную корзину', () => {
    testSuite.clearCart();
    const testCart = ['product1', 'product2'];
    saveCart(testCart);
    const retrievedCart = getCart();
    return JSON.stringify(testCart) === JSON.stringify(retrievedCart);
});

testSuite.addTest('getCart() обрабатывает некорректные данные в localStorage', () => {
    localStorage.setItem('cart', 'invalid json');
    const cart = getCart();
    return Array.isArray(cart) && cart.length === 0;
});

testSuite.addTest('getCart() обрабатывает null в localStorage', () => {
    localStorage.setItem('cart', null);
    const cart = getCart();
    return Array.isArray(cart) && cart.length === 0;
});

// Тесты для функций корзины
testSuite.addTest('addToCart() добавляет товар в корзину', () => {
    testSuite.clearCart();
    addToCart('test-product-1');
    const cart = getCart();
    return cart.includes('test-product-1') && cart.length === 1;
});

testSuite.addTest('addToCart() не добавляет дубликаты', () => {
    testSuite.clearCart();
    addToCart('test-product-1');
    addToCart('test-product-1');
    const cart = getCart();
    return cart.length === 1 && cart.filter(id => id === 'test-product-1').length === 1;
});

testSuite.addTest('addToCart() добавляет множественные товары', () => {
    testSuite.clearCart();
    addToCart('product-1');
    addToCart('product-2');
    addToCart('product-3');
    const cart = getCart();
    return cart.length === 3 && 
           cart.includes('product-1') && 
           cart.includes('product-2') && 
           cart.includes('product-3');
});

testSuite.addTest('updateCartCount() обновляет счетчик корзины', () => {
    testSuite.createMockDOM();
    testSuite.clearCart();
    
    addToCart('test-product-1');
    addToCart('test-product-2');
    updateCartCount();
    
    const countElement = document.getElementById('cart-count');
    const result = countElement && countElement.textContent === '2';
    
    testSuite.cleanupMockDOM();
    return result;
});

testSuite.addTest('updateCartCount() работает с пустой корзиной', () => {
    testSuite.createMockDOM();
    testSuite.clearCart();
    
    updateCartCount();
    
    const countElement = document.getElementById('cart-count');
    const result = countElement && countElement.textContent === '0';
    
    testSuite.cleanupMockDOM();
    return result;
});

// Тесты для обработчиков событий
testSuite.addTest('Обработчик клика работает с кнопками с data-product-id', () => {
    testSuite.createMockDOM();
    testSuite.clearCart();
    
    const button = document.querySelector('.add-to-cart-btn[data-product-id="test-1"]');
    if (!button) return false;
    
    button.click();
    const cart = getCart();
    const result = cart.includes('test-1');
    
    testSuite.cleanupMockDOM();
    return result;
});

testSuite.addTest('Обработчик клика работает с делегированием событий', () => {
    testSuite.createMockDOM();
    testSuite.clearCart();
    
    const button = document.querySelector('.add-to-cart-btn[data-product-id="test-2"]');
    if (!button) return false;
    
    button.click();
    const cart = getCart();
    const result = cart.includes('test-2') && cart.length === 1;
    
    testSuite.cleanupMockDOM();
    return result;
});

testSuite.addTest('Обработчик клика обновляет счетчик', () => {
    testSuite.createMockDOM();
    testSuite.clearCart();
    
    const initialCount = document.getElementById('cart-count').textContent;
    const button = document.querySelector('.add-to-cart-btn[data-product-id="test-3"]');
    if (!button) return false;
    
    button.click();
    const newCount = document.getElementById('cart-count').textContent;
    const result = parseInt(newCount) > parseInt(initialCount);
    
    testSuite.cleanupMockDOM();
    return result;
});

// Тесты для граничных случаев
testSuite.addTest('addToCart() работает с пустой строкой', () => {
    testSuite.clearCart();
    addToCart('');
    const cart = getCart();
    return cart.includes('') && cart.length === 1;
});

testSuite.addTest('addToCart() работает с числовыми ID', () => {
    testSuite.clearCart();
    addToCart('123');
    addToCart('456');
    const cart = getCart();
    return cart.includes('123') && cart.includes('456') && cart.length === 2;
});

testSuite.addTest('addToCart() работает с специальными символами', () => {
    testSuite.clearCart();
    addToCart('product-with-special-chars-!@#$%');
    const cart = getCart();
    return cart.includes('product-with-special-chars-!@#$%') && cart.length === 1;
});

// Тесты производительности
testSuite.addTest('addToCart() работает быстро с большим количеством товаров', () => {
    testSuite.clearCart();
    
    const startTime = performance.now();
    for (let i = 0; i < 100; i++) {
        addToCart(`product-${i}`);
    }
    const endTime = performance.now();
    
    const cart = getCart();
    const executionTime = endTime - startTime;
    
    return cart.length === 100 && executionTime < 100; // Должно выполняться менее чем за 100мс
});

// Тесты совместимости
testSuite.addTest('Функции работают без ошибок при отсутствии localStorage', () => {
    const originalLocalStorage = window.localStorage;
    delete window.localStorage;
    
    try {
        const cart = getCart();
        saveCart(['test']);
        const result = Array.isArray(cart);
        
        window.localStorage = originalLocalStorage;
        return result;
    } catch (error) {
        window.localStorage = originalLocalStorage;
        return false;
    }
});

// Экспортируем функции для использования в браузере
if (typeof window !== 'undefined') {
    window.CartTestSuite = CartTestSuite;
    window.runCartTests = () => testSuite.runAllTests();
}

// Автоматический запуск тестов в Node.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { CartTestSuite, testSuite };
}
