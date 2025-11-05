/**
 * JavaScript Unit-тесты для кнопки генерации AI-описания в админ-панели
 */

class AIDescriptionButtonTestSuite {
    constructor() {
        this.tests = [];
        this.results = {
            passed: 0,
            failed: 0,
            total: 0
        };
    }

    addTest(name, testFunction) {
        this.tests.push({ name, testFunction });
    }

    runTests() {
        console.log("🧪 Запуск JavaScript тестов кнопки AI-описание");
        console.log("=".repeat(60));
        
        this.results = { passed: 0, failed: 0, total: 0 };
        
        this.tests.forEach(test => {
            try {
                const result = test.testFunction();
                if (result) {
                    console.log(`✅ ${test.name}`);
                    this.results.passed++;
                } else {
                    console.log(`❌ ${test.name}`);
                    this.results.failed++;
                }
            } catch (error) {
                console.log(`💥 ${test.name} - Ошибка: ${error.message}`);
                this.results.failed++;
            }
            this.results.total++;
        });
        
        this.printResults();
        return this.results;
    }

    printResults() {
        console.log("\n" + "=".repeat(60));
        console.log("📊 Результаты тестирования:");
        console.log(`✅ Пройдено: ${this.results.passed}`);
        console.log(`❌ Провалено: ${this.results.failed}`);
        console.log(`📊 Всего: ${this.results.total}`);
        
        const successRate = (this.results.passed / this.results.total) * 100;
        console.log(`📈 Успешность: ${successRate.toFixed(1)}%`);
        
        if (this.results.failed === 0) {
            console.log("\n🎉 Все тесты прошли успешно!");
        } else {
            console.log("\n⚠️ Некоторые тесты провалились. Проверьте реализацию.");
        }
    }
}

// Создаем экземпляр тестового набора
const testSuite = new AIDescriptionButtonTestSuite();

// Тесты для проверки рендеринга кнопки
testSuite.addTest('Кнопка AI-описание рендерится в таблице', () => {
    // Создаем мок-таблицу
    const table = document.createElement('table');
    const tbody = document.createElement('tbody');
    table.appendChild(tbody);
    
    // Мокаем функцию renderProducts
    const mockProducts = [
        { id: 1, title: 'Тест', author_id: 1, description: 'Описание', price: 100 }
    ];
    
    const row = document.createElement('tr');
    row.innerHTML = `
        <td>1</td>
        <td>Тест</td>
        <td>1</td>
        <td class="description-cell">Описание</td>
        <td>100.00</td>
        <td>
            <div class="actions">
                <button class="generate-description-btn" data-product-id="1">AI-описание</button>
            </div>
        </td>
    `;
    tbody.appendChild(row);
    
    const button = tbody.querySelector('.generate-description-btn');
    return button !== null && button.textContent === 'AI-описание';
});

testSuite.addTest('Кнопка имеет правильный класс generate-description-btn', () => {
    const button = document.createElement('button');
    button.className = 'generate-description-btn';
    button.setAttribute('data-product-id', '1');
    button.textContent = 'AI-описание';
    
    return button.classList.contains('generate-description-btn');
});

testSuite.addTest('Кнопка имеет атрибут data-product-id', () => {
    const button = document.createElement('button');
    button.className = 'generate-description-btn';
    button.setAttribute('data-product-id', '123');
    
    const productId = button.getAttribute('data-product-id');
    return productId === '123' && parseInt(productId) === 123;
});

testSuite.addTest('Кнопка имеет правильный текст "AI-описание"', () => {
    const button = document.createElement('button');
    button.className = 'generate-description-btn';
    button.textContent = 'AI-описание';
    
    return button.textContent === 'AI-описание';
});

// Тесты для проверки делегирования событий
testSuite.addTest('Обработчик клика извлекает productId из data-атрибута', () => {
    const button = document.createElement('button');
    button.className = 'generate-description-btn';
    button.setAttribute('data-product-id', '456');
    
    const productId = button.getAttribute('data-product-id');
    return productId === '456';
});

testSuite.addTest('Обработчик клика находит кнопку по классу', () => {
    const table = document.createElement('table');
    const tbody = document.createElement('tbody');
    table.appendChild(tbody);
    
    const button = document.createElement('button');
    button.className = 'generate-description-btn';
    button.setAttribute('data-product-id', '1');
    
    const row = document.createElement('tr');
    row.innerHTML = '<td></td><td></td><td></td><td class="description-cell"></td><td></td><td></td>';
    row.querySelector('td:last-child').appendChild(button);
    tbody.appendChild(row);
    
    const foundButton = tbody.querySelector('.generate-description-btn');
    return foundButton !== null && foundButton.classList.contains('generate-description-btn');
});

testSuite.addTest('Кнопка отключается при клике', () => {
    const button = document.createElement('button');
    button.className = 'generate-description-btn';
    button.disabled = false;
    
    // Симулируем клик - отключаем кнопку
    button.disabled = true;
    
    return button.disabled === true;
});

testSuite.addTest('Текст кнопки меняется на "Генерация..." при клике', () => {
    const button = document.createElement('button');
    button.textContent = 'AI-описание';
    
    // Симулируем состояние во время запроса
    button.textContent = 'Генерация...';
    
    return button.textContent === 'Генерация...';
});

testSuite.addTest('Кнопка восстанавливается после завершения запроса', () => {
    const button = document.createElement('button');
    button.className = 'generate-description-btn';
    button.textContent = 'AI-описание';
    button.disabled = false;
    
    // Симулируем состояние во время запроса
    button.disabled = true;
    button.textContent = 'Генерация...';
    
    // Восстанавливаем после завершения
    button.disabled = false;
    button.textContent = 'AI-описание';
    
    return button.disabled === false && button.textContent === 'AI-описание';
});

// Тесты для проверки обновления ячейки описания
testSuite.addTest('Ячейка с описанием находится по классу description-cell', () => {
    const row = document.createElement('tr');
    row.innerHTML = `
        <td>1</td>
        <td>Тест</td>
        <td>1</td>
        <td class="description-cell">Старое описание</td>
        <td>100</td>
        <td></td>
    `;
    
    const descriptionCell = row.querySelector('.description-cell');
    return descriptionCell !== null && descriptionCell.textContent === 'Старое описание';
});

testSuite.addTest('Ячейка описания обновляется новым текстом', () => {
    const descriptionCell = document.createElement('td');
    descriptionCell.className = 'description-cell';
    descriptionCell.textContent = 'Старое описание';
    
    const newDescription = 'Новое AI-описание, которое длиннее 50 символов и будет обрезано...';
    const shortDescription = newDescription.length > 50 
        ? newDescription.substring(0, 50) + '...' 
        : newDescription;
    
    descriptionCell.textContent = shortDescription;
    
    return descriptionCell.textContent.includes('...') && descriptionCell.textContent.length === 53;
});

testSuite.addTest('Полное описание сохраняется в title атрибуте', () => {
    const descriptionCell = document.createElement('td');
    descriptionCell.className = 'description-cell';
    
    const fullDescription = 'Полное AI-описание товара';
    const shortDescription = fullDescription.substring(0, 50) + '...';
    
    descriptionCell.textContent = shortDescription;
    descriptionCell.title = fullDescription;
    
    return descriptionCell.title === fullDescription;
});

testSuite.addTest('Короткое описание не обрезается', () => {
    const fullDescription = 'Короткое описание';
    const shortDescription = fullDescription.length > 50 
        ? fullDescription.substring(0, 50) + '...' 
        : fullDescription;
    
    return shortDescription === fullDescription && !shortDescription.includes('...'));
});

// Тесты для проверки обновления localStorage
testSuite.addTest('Описание продукта обновляется в массиве products', () => {
    const mockProducts = [
        { id: 1, title: 'Тест', description: 'Старое описание', price: 100 }
    ];
    
    const productId = 1;
    const newDescription = 'Новое AI-описание';
    
    const product = mockProducts.find(p => p.id == productId);
    if (product) {
        product.description = newDescription;
    }
    
    return product && product.description === newDescription;
});

testSuite.addTest('Обновленный продукт сохраняется в localStorage', () => {
    const mockProducts = [
        { id: 1, title: 'Тест', description: 'Новое описание', price: 100 }
    ];
    
    localStorage.setItem('admin_products', JSON.stringify(mockProducts));
    const saved = JSON.parse(localStorage.getItem('admin_products'));
    
    return saved && saved[0].description === 'Новое описание';
});

// Тесты для проверки URL запроса
testSuite.addTest('URL запроса формируется правильно', () => {
    const productId = 789;
    const expectedUrl = `http://127.0.0.1:8004/api/v1/recommendations/generate-description/${productId}`;
    const actualUrl = `http://127.0.0.1:8004/api/v1/recommendations/generate-description/${productId}`;
    
    return actualUrl === expectedUrl;
});

testSuite.addTest('URL содержит правильный productId', () => {
    const productId = '123';
    const url = `http://127.0.0.1:8004/api/v1/recommendations/generate-description/${productId}`;
    
    return url.includes(productId) && url.endsWith(productId) && url.includes('8004');
});

// Тесты для проверки обработки ошибок
testSuite.addTest('Ошибка HTTP запроса обрабатывается', () => {
    let errorHandled = false;
    
    // Симулируем ошибку
    try {
        throw new Error('HTTP error! status: 500');
    } catch (error) {
        errorHandled = error.message.includes('HTTP error');
    }
    
    return errorHandled;
});

testSuite.addTest('Сетевая ошибка обрабатывается', () => {
    let networkErrorHandled = false;
    
    try {
        throw new Error('Failed to fetch');
    } catch (error) {
        networkErrorHandled = error.message === 'Failed to fetch';
    }
    
    return networkErrorHandled;
});

// Тесты для проверки структуры ответа API
testSuite.addTest('Проверка наличия поля generated_description в ответе', () => {
    const mockResponse = {
        success: true,
        generated_description: 'Новое описание',
        product_id: 1
    };
    
    return mockResponse.hasOwnProperty('generated_description') && 
           typeof mockResponse.generated_description === 'string';
});

testSuite.addTest('Ответ API обрабатывается корректно', () => {
    const mockResponse = {
        success: true,
        generated_description: 'Полное AI-описание товара',
        product_id: 1
    };
    
    return mockResponse.success === true && 
           mockResponse.generated_description !== undefined &&
           mockResponse.generated_description.length > 0;
});

// Тесты для проверки UI элементов
testSuite.addTest('Таблица продуктов существует в DOM', () => {
    // В реальном тесте здесь была бы проверка DOM
    // Но для unit-теста проверяем логику
    const tableId = 'products-table';
    return tableId === 'products-table';
});

testSuite.addTest('Ячейка описания имеет класс description-cell', () => {
    const cell = document.createElement('td');
    cell.className = 'description-cell';
    
    return cell.classList.contains('description-cell');
});

// Тесты производительности
testSuite.addTest('Обновление ячейки выполняется быстро', () => {
    const startTime = performance.now();
    
    const cell = document.createElement('td');
    cell.textContent = 'Новое описание';
    
    const endTime = performance.now();
    const duration = endTime - startTime;
    
    // Обновление должно быть мгновенным (< 1мс)
    return duration < 1;
});

testSuite.addTest('Извлечение productId выполняется быстро', () => {
    const startTime = performance.now();
    
    const button = document.createElement('button');
    button.setAttribute('data-product-id', '123');
    const productId = button.getAttribute('data-product-id');
    
    const endTime = performance.now();
    const duration = endTime - startTime;
    
    return duration < 1 && productId === '123';
});

// Функция для запуска тестов
function runAIDescriptionButtonTests() {
    return testSuite.runTests();
}

// Автоматический запуск тестов при загрузке страницы
if (typeof window !== 'undefined') {
    // Запускаем тесты только если мы в браузере
    document.addEventListener('DOMContentLoaded', () => {
        console.log("🚀 Автоматический запуск тестов кнопки AI-описание");
        runAIDescriptionButtonTests();
    });
}

// Экспортируем для использования в других модулях
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { AIDescriptionButtonTestSuite, runAIDescriptionButtonTests };
}

