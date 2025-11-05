// Конфигурация API (используем единую конфигурацию)
// Если api-config.js не загружен, используем fallback
if (typeof window.API_CONFIG === 'undefined') {
    window.API_CONFIG = {
        cart: 'http://localhost:8005',
        orders: 'http://localhost:8002'
    };
}
// Используем window.API_CONFIG напрямую без переобъявления
// Это предотвращает ошибку "Identifier 'API_CONFIG' has already been declared"

// Моковые данные для fallback режима (обновлены на виниловые пластинки)
const MOCK_PRODUCTS = {
    "1": {
        id: "1",
        title: "Abbey Road",
        artist: "The Beatles",
        author: "The Beatles", // Для обратной совместимости
        price: 29.99,
        image_url: "https://via.placeholder.com/600/4169E1/FFFFFF?text=Abbey+Road",
        genre: "rock"
    },
    "2": {
        id: "2",
        title: "Sgt. Pepper's Lonely Hearts Club Band",
        artist: "The Beatles",
        author: "The Beatles",
        price: 32.99,
        image_url: "https://via.placeholder.com/600/4169E1/FFFFFF?text=Sgt.+Pepper",
        genre: "rock"
    },
    "3": {
        id: "3",
        title: "The White Album",
        artist: "The Beatles",
        author: "The Beatles",
        price: 39.99,
        image_url: "https://via.placeholder.com/600/FFFFFF/000000?text=White+Album",
        genre: "rock"
    },
    "4": {
        id: "4",
        title: "Revolver",
        artist: "The Beatles",
        author: "The Beatles",
        price: 28.99,
        image_url: "https://via.placeholder.com/600/FF6B6B/FFFFFF?text=Revolver",
        genre: "rock"
    },
    "5": {
        id: "5",
        title: "The Dark Side of the Moon",
        artist: "Pink Floyd",
        author: "Pink Floyd",
        price: 34.99,
        image_url: "https://via.placeholder.com/600/000000/FFFFFF?text=Dark+Side+Moon",
        genre: "progressive"
    },
    "6": {
        id: "6",
        title: "The Wall",
        artist: "Pink Floyd",
        author: "Pink Floyd",
        price: 44.99,
        image_url: "https://via.placeholder.com/600/FFA500/000000?text=The+Wall",
        genre: "progressive"
    },
    "7": {
        id: "7",
        title: "Wish You Were Here",
        artist: "Pink Floyd",
        author: "Pink Floyd",
        price: 31.99,
        image_url: "https://via.placeholder.com/600/FFD700/000000?text=Wish+You+Were+Here",
        genre: "progressive"
    },
    "8": {
        id: "8",
        title: "Led Zeppelin IV",
        artist: "Led Zeppelin",
        author: "Led Zeppelin",
        price: 32.99,
        image_url: "https://via.placeholder.com/600/8B4513/FFFFFF?text=Led+Zeppelin+IV",
        genre: "rock"
    },
    "9": {
        id: "9",
        title: "Physical Graffiti",
        artist: "Led Zeppelin",
        author: "Led Zeppelin",
        price: 38.99,
        image_url: "https://via.placeholder.com/600/696969/FFFFFF?text=Physical+Graffiti",
        genre: "rock"
    },
    "10": {
        id: "10",
        title: "A Night at the Opera",
        artist: "Queen",
        author: "Queen",
        price: 31.99,
        image_url: "https://via.placeholder.com/600/DC143C/FFFFFF?text=Night+at+Opera",
        genre: "rock"
    },
    "11": {
        id: "11",
        title: "News of the World",
        artist: "Queen",
        author: "Queen",
        price: 29.99,
        image_url: "https://via.placeholder.com/600/C71585/FFFFFF?text=News+World",
        genre: "rock"
    },
    "12": {
        id: "12",
        title: "Sticky Fingers",
        artist: "The Rolling Stones",
        author: "The Rolling Stones",
        price: 33.99,
        image_url: "https://via.placeholder.com/600/FF4500/FFFFFF?text=Sticky+Fingers",
        genre: "rock"
    },
    "13": {
        id: "13",
        title: "Exile on Main St.",
        artist: "The Rolling Stones",
        author: "The Rolling Stones",
        price: 39.99,
        image_url: "https://via.placeholder.com/600/2F4F4F/FFFFFF?text=Exile+Main+St",
        genre: "rock"
    },
    "14": {
        id: "14",
        title: "The Doors",
        artist: "The Doors",
        author: "The Doors",
        price: 27.99,
        image_url: "https://via.placeholder.com/600/9932CC/FFFFFF?text=The+Doors",
        genre: "rock"
    },
    "15": {
        id: "15",
        title: "Back in Black",
        artist: "AC/DC",
        author: "AC/DC",
        price: 30.99,
        image_url: "https://via.placeholder.com/600/000000/FFFFFF?text=Back+in+Black",
        genre: "rock"
    },
    "16": {
        id: "16",
        title: "Paranoid",
        artist: "Black Sabbath",
        author: "Black Sabbath",
        price: 28.99,
        image_url: "https://via.placeholder.com/600/808080/FFFFFF?text=Paranoid",
        genre: "rock"
    },
    "17": {
        id: "17",
        title: "The Rise and Fall of Ziggy Stardust",
        artist: "David Bowie",
        author: "David Bowie",
        price: 32.99,
        image_url: "https://via.placeholder.com/600/FF1493/FFFFFF?text=Ziggy+Stardust",
        genre: "rock"
    },
    "18": {
        id: "18",
        title: "Highway 61 Revisited",
        artist: "Bob Dylan",
        author: "Bob Dylan",
        price: 29.99,
        image_url: "https://via.placeholder.com/600/DEB887/000000?text=Highway+61",
        genre: "rock"
    },
    "19": {
        id: "19",
        title: "Tommy",
        artist: "The Who",
        author: "The Who",
        price: 35.99,
        image_url: "https://via.placeholder.com/600/4682B4/FFFFFF?text=Tommy",
        genre: "rock"
    },
    "20": {
        id: "20",
        title: "Machine Head",
        artist: "Deep Purple",
        author: "Deep Purple",
        price: 30.99,
        image_url: "https://via.placeholder.com/600/800080/FFFFFF?text=Machine+Head",
        genre: "rock"
    },
    "21": {
        id: "21",
        title: "Are You Experienced",
        artist: "Jimi Hendrix",
        author: "Jimi Hendrix",
        price: 31.99,
        image_url: "https://via.placeholder.com/600/FF6347/FFFFFF?text=Are+You+Experienced",
        genre: "rock"
    },
    "22": {
        id: "22",
        title: "London Calling",
        artist: "The Clash",
        author: "The Clash",
        price: 33.99,
        image_url: "https://via.placeholder.com/600/B22222/FFFFFF?text=London+Calling",
        genre: "rock"
    }
};

// Функция для отображения ошибки
function showError(message) {
    const errorElement = document.getElementById('error-message');
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.style.display = 'block';
    }
}

// Функция для скрытия ошибки
function hideError() {
    const errorElement = document.getElementById('error-message');
    if (errorElement) {
        errorElement.style.display = 'none';
    }
}

// Функция для получения товаров из корзины
function getCartItems() {
    const cart = localStorage.getItem('cart');
    return cart ? JSON.parse(cart) : [];
}

// Функция для миграции данных из старой системы корзины
function migrateCartData() {
    const oldCart = localStorage.getItem('cart');
    const cartWithQuantity = getCartWithQuantity();
    
    if (oldCart && !Object.keys(cartWithQuantity).length) {
        try {
            const oldCartItems = JSON.parse(oldCart);
            const newCartWithQuantity = {};
            
            // Конвертируем старые данные в новый формат
            if (Array.isArray(oldCartItems)) {
                oldCartItems.forEach(item => {
                    // Если это объект с id, используем id
                    const productId = typeof item === 'object' && item.id ? item.id : item;
                    const normalizedId = String(productId);
                    
                    // Пропускаем некорректные ID
                    if (normalizedId !== '[object Object]' && normalizedId !== 'undefined' && normalizedId !== 'null') {
                        newCartWithQuantity[normalizedId] = (newCartWithQuantity[normalizedId] || 0) + 1;
                    } else {
                        console.warn('Пропущен некорректный ID при миграции:', productId);
                    }
                });
            }
            
            // Сохраняем в новом формате
            saveCartWithQuantity(newCartWithQuantity);
            
            // Очищаем старые данные
            localStorage.removeItem('cart');
            
            console.log('Данные корзины мигрированы:', newCartWithQuantity);
        } catch (error) {
            console.error('Ошибка при миграции данных корзины:', error);
        }
    }
}

// Функция для очистки некорректных записей из корзины
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
        console.log('Очищены некорректные записи из корзины');
        saveCartWithQuantity(cleanedCart);
    }
}

// Функция для получения корзины в новом формате (с количеством)
function getCartWithQuantity() {
    const cart = localStorage.getItem('cartWithQuantity');
    return cart ? JSON.parse(cart) : {};
}

// Функция для сохранения корзины с количеством
function saveCartWithQuantity(cartWithQuantity) {
    localStorage.setItem('cartWithQuantity', JSON.stringify(cartWithQuantity));
    updateCartCount();
}

// Функция для очистки корзины
function clearCart() {
    localStorage.removeItem('cart');
    localStorage.removeItem('cartWithQuantity');
    updateCartCount();
    
    // Перезагружаем корзину для обновления отображения
    loadCart();
}

// Функция для обновления счетчика корзины
function updateCartCount() {
    const cartWithQuantity = getCartWithQuantity();
    const totalItems = Object.values(cartWithQuantity).reduce((sum, quantity) => sum + quantity, 0);
    const cartCountElement = document.getElementById('cart-count');
    if (cartCountElement) {
        cartCountElement.textContent = totalItems;
    }
}

// Функция для расчета стоимости корзины (с fallback)
async function calculateCartTotal() {
    const cartWithQuantity = getCartWithQuantity();
    const productIds = Object.keys(cartWithQuantity);
    
    console.log('Данные корзины для расчета:', cartWithQuantity);
    console.log('ID товаров для отправки:', productIds);
    console.log('localStorage cartWithQuantity:', localStorage.getItem('cartWithQuantity'));
    
    if (productIds.length === 0) {
        return { items: [], total: 0 };
    }

    try {
        console.log('Отправка запроса к Cart Service...');
        const response = await fetch(`${window.API_CONFIG.cart}/api/v1/cart/calculate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                product_ids: productIds
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('Ответ от Cart Service:', data);
        
        // Проверяем, все ли товары найдены
        const foundItemIds = data.items.map(item => item.id);
        const missingItemIds = productIds.filter(id => !foundItemIds.includes(id));
        
        if (missingItemIds.length > 0) {
            console.warn('Некоторые товары не найдены в Cart Service:', missingItemIds);
            // Показываем предупреждение пользователю
            showError(`Внимание: ${missingItemIds.length} товар(ов) временно недоступен(ы) и не включен(ы) в расчет.`);
        }
        
        // Обновляем данные с учетом количества и нормализуем формат
        const itemsWithQuantity = data.items.map(item => ({
            ...item,
            id: String(item.id), // Нормализуем ID к строке
            title: item.title || item.name,
            price: item.price,
            image_url: item.image_url || item.cover_url || item.cover_image_url || '',
            artist: item.artist || item.author || 'Неизвестный исполнитель',
            author: item.artist || item.author || 'Неизвестный исполнитель', // Для обратной совместимости
            quantity: cartWithQuantity[String(item.id)] || cartWithQuantity[item.id] || 1,
            total_price: item.price * (cartWithQuantity[String(item.id)] || cartWithQuantity[item.id] || 1)
        }));
        
        const total = itemsWithQuantity.reduce((sum, item) => sum + item.total_price, 0);
        
        return { items: itemsWithQuantity, total };
    } catch (error) {
        console.warn('Ошибка при обращении к Cart Service, используем fallback режим:', error.message);
        
        // Fallback режим - используем сохраненную информацию о товарах или моковые данные
        const items = [];
        let total = 0;
        
        // Сначала пытаемся получить информацию из localStorage
        let productsInfo = {};
        try {
            const stored = localStorage.getItem('productsInfo');
            if (stored) {
                productsInfo = JSON.parse(stored);
            }
        } catch (e) {
            console.warn('Ошибка при чтении productsInfo:', e);
        }
        
        // Если нет данных в localStorage, пытаемся получить из API каталога
        for (const productId of productIds) {
            const quantity = cartWithQuantity[productId];
            let productData = null;
            
            // Пытаемся получить из сохраненной информации
            if (productsInfo[productId]) {
                productData = productsInfo[productId];
            } else if (MOCK_PRODUCTS[productId]) {
                // Используем моковые данные как последний вариант
                const mock = MOCK_PRODUCTS[productId];
                productData = {
                    id: mock.id,
                    title: mock.title,
                    price: mock.price,
                    image_url: mock.image_url || '',
                    artist: mock.artist || mock.author || 'Неизвестный исполнитель',
                    author: mock.artist || mock.author || 'Неизвестный исполнитель' // Для обратной совместимости
                };
            } else {
                // Пытаемся получить из API каталога синхронно (только если уже загружен)
                if (window.vinylRecords && Array.isArray(window.vinylRecords)) {
                    const record = window.vinylRecords.find(r => String(r.id) === String(productId));
                    if (record) {
                        productData = {
                            id: record.id,
                            title: record.title || record.name,
                            price: record.price,
                            image_url: record.image || record.cover_url || '',
                            author: record.artist || record.author || 'Неизвестный исполнитель'
                        };
                        // Сохраняем для будущего использования
                        productsInfo[productId] = productData;
                        localStorage.setItem('productsInfo', JSON.stringify(productsInfo));
                    }
                }
            }
            
            if (productData) {
                const item = {
                    ...productData,
                    quantity: quantity,
                    total_price: productData.price * quantity
                };
                items.push(item);
                total += item.total_price;
            } else {
                console.warn('Товар с ID', productId, 'не найден в доступных данных');
            }
        }
        
        return { items, total };
    }
}

// Функция для отображения товаров в корзине
function renderCartItems(items) {
    const cartItemsContainer = document.getElementById('cart-items');
    const cartSummary = document.getElementById('cart-summary');
    
    if (!cartItemsContainer) return;

    if (items.length === 0) {
        cartItemsContainer.innerHTML = `
            <div class="empty-cart">
                <h2>Корзина пуста</h2>
                <p>Добавьте товары в корзину, чтобы продолжить покупки</p>
                <a href="index.html">Перейти к каталогу</a>
            </div>
        `;
        cartSummary.style.display = 'none';
        return;
    }

    // Отображаем товары с количеством и кнопками управления
    cartItemsContainer.innerHTML = items.map(item => `
        <div class="cart-item" data-product-id="${item.id}">
            <img src="${item.image_url || 'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=80&h=80&fit=crop'}" alt="${item.title}">
            <div class="cart-item-info">
                <div class="cart-item-title">${item.title}</div>
                <div class="cart-item-author">${item.artist || item.author || 'Неизвестный исполнитель'}</div>
                <div class="cart-item-price">${item.price} ₽</div>
            </div>
            <div class="cart-item-controls">
                <div class="quantity-controls">
                    <button class="quantity-btn minus-btn" onclick="changeQuantity('${item.id}', -1)">-</button>
                    <span class="quantity-display">${item.quantity}</span>
                    <button class="quantity-btn plus-btn" onclick="changeQuantity('${item.id}', 1)">+</button>
                </div>
                <div class="item-total">${item.total_price} ₽</div>
                <button class="remove-btn" onclick="removeFromCart('${item.id}')">Удалить</button>
            </div>
        </div>
    `).join('');

    cartSummary.style.display = 'block';
}

// Функция для изменения количества товара
function changeQuantity(productId, change) {
    const cartWithQuantity = getCartWithQuantity();
    const currentQuantity = cartWithQuantity[productId] || 0;
    const newQuantity = Math.max(0, currentQuantity + change);
    
    if (newQuantity === 0) {
        // Удаляем товар из корзины если количество стало 0
        delete cartWithQuantity[productId];
    } else {
        cartWithQuantity[productId] = newQuantity;
    }
    
    saveCartWithQuantity(cartWithQuantity);
    
    // Перезагружаем корзину для обновления отображения
    loadCart();
}

// Функция для удаления товара из корзины
function removeFromCart(productId) {
    const cartWithQuantity = getCartWithQuantity();
    delete cartWithQuantity[productId];
    saveCartWithQuantity(cartWithQuantity);
    
    // Перезагружаем корзину для обновления отображения
    loadCart();
}

// Функция для добавления товара в корзину (обновленная)
function addToCartWithQuantity(productId) {
    // Убеждаемся, что productId является строкой
    const normalizedId = String(productId);
    console.log('addToCartWithQuantity вызвана с ID:', productId, 'нормализованный ID:', normalizedId);
    
    // Проверяем, что ID не является [object Object]
    if (normalizedId === '[object Object]') {
        console.error('Обнаружен некорректный ID [object Object], пропускаем добавление');
        return;
    }
    
    // Мигрируем данные перед добавлением
    migrateCartData();
    
    const cartWithQuantity = getCartWithQuantity();
    console.log('Корзина до добавления:', cartWithQuantity);
    cartWithQuantity[normalizedId] = (cartWithQuantity[normalizedId] || 0) + 1;
    console.log('Корзина после добавления:', cartWithQuantity);
    saveCartWithQuantity(cartWithQuantity);
    console.log('Корзина сохранена в localStorage');
    
    // Обновляем счетчик корзины
    updateCartCount();
    
    // Показываем уведомление пользователю
    const button = document.querySelector(`[data-product-id="${normalizedId}"] .add-to-cart-btn, .add-to-cart-btn[data-product-id="${normalizedId}"]`);
    if (button) {
        const originalText = button.textContent;
        button.textContent = 'Добавлено!';
        button.style.backgroundColor = '#28a745';
        
        setTimeout(() => {
            button.textContent = originalText;
            button.style.backgroundColor = '';
        }, 2000);
    }
}

// Экспортируем функции в глобальную область видимости
window.addToCartWithQuantity = addToCartWithQuantity;
window.getCartWithQuantity = getCartWithQuantity;
window.saveCartWithQuantity = saveCartWithQuantity;
window.updateCartCount = updateCartCount;
window.migrateCartData = migrateCartData;
window.clearCart = clearCart;
window.createOrder = createOrder;

// Функция для обновления итоговой суммы
function updateTotalPrice(total) {
    const totalPriceElement = document.getElementById('total-price');
    if (totalPriceElement) {
        totalPriceElement.textContent = total;
    }
}

// Функция для оформления заказа (только для авторизованных пользователей)
async function createOrder() {
    const cartWithQuantity = getCartWithQuantity();
    const productIds = Object.keys(cartWithQuantity);
    
    if (productIds.length === 0) {
        alert('Корзина пуста!');
        return;
    }

    // Проверяем авторизацию (обязательно для оформления заказа)
    const accessToken = localStorage.getItem('accessToken');
    if (!accessToken) {
        alert('🎵 Для оформления заказа необходимо войти в систему\n\nМы сохранили вашу корзину - просто войдите или зарегистрируйтесь, чтобы продолжить покупку!');
        window.location.href = 'login.html';
        return;
    }

    const checkoutBtn = document.getElementById('checkout-btn');
    if (checkoutBtn) {
        checkoutBtn.disabled = true;
        checkoutBtn.textContent = 'Оформление заказа...';
    }

    try {
        console.log('Отправка заказа в Orders Service...', {
            product_ids: productIds,
            quantities: cartWithQuantity
        });
        
        const headers = {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${accessToken}` // Обязательный заголовок
        };
        
        const response = await fetch(`${window.API_CONFIG.orders}/api/v1/orders`, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({
                product_ids: productIds,
                quantities: cartWithQuantity
            })
        });

        if (!response.ok) {
            let errorMessage = `Ошибка при создании заказа (код: ${response.status})`;
            
            try {
                const errorData = await response.json();
                errorMessage = errorData.detail || errorMessage;
            } catch (e) {
                // Если не удалось распарсить JSON, используем стандартное сообщение
            }
            
            // Обработка ошибок авторизации
            if (response.status === 401) {
                // Улучшаем сообщение для пользователя
                let friendlyMessage = 'Ваша сессия истекла или требуется авторизация.';
                if (errorMessage.includes('сессия истекла') || errorMessage.includes('сессия')) {
                    friendlyMessage = 'Ваша сессия истекла.';
                } else if (errorMessage.includes('войти') || errorMessage.includes('авторизац')) {
                    friendlyMessage = 'Для оформления заказа необходимо войти в систему.';
                }
                
                alert('🔐 ' + friendlyMessage + '\n\n✅ Ваша корзина сохранена!\n\nПожалуйста, войдите в систему снова, чтобы продолжить оформление заказа.');
                localStorage.removeItem('accessToken');
                window.location.href = 'login.html';
                return;
            }
            
            throw new Error(errorMessage);
        }

        const orderData = await response.json();
        console.log('Заказ создан:', orderData);
        
        // Очищаем корзину после успешного заказа
        clearCart();
        
        // Показываем детальное сообщение об успехе
        const totalItems = orderData.total_items || Object.values(cartWithQuantity).reduce((sum, q) => sum + q, 0);
        alert(`✅ Заказ №${orderData.order_id} успешно оформлен!\n\n📦 Товаров: ${totalItems}\n📅 Время: ${new Date().toLocaleString()}\n\n📧 На вашу почту отправлено письмо с деталями заказа, мнением музыкального эксперта и персональными рекомендациями!`);
        
        // Перенаправляем на главную страницу
        window.location.href = 'index.html';
        
    } catch (error) {
        console.error('Ошибка при создании заказа:', error);
        
        // Показываем дружелюбное сообщение об ошибке
        let errorMessage = error.message || 'Неизвестная ошибка';
        
        // Улучшаем сообщения для пользователя
        if (errorMessage.includes('авторизац') || errorMessage.includes('войти')) {
            errorMessage = 'Для оформления заказа необходимо войти в систему. Пожалуйста, войдите и попробуйте еще раз.';
        } else if (errorMessage.includes('сеть') || errorMessage.includes('network')) {
            errorMessage = 'Проблема с подключением к серверу. Проверьте интернет-соединение и попробуйте еще раз.';
        } else {
            errorMessage = 'К сожалению, произошла ошибка при оформлении заказа. Пожалуйста, попробуйте еще раз или обратитесь в поддержку.';
        }
        
        alert('⚠️ ' + errorMessage + '\n\n✅ Ваша корзина сохранена, ничего не потеряно!');
        
    } finally {
        if (checkoutBtn) {
            checkoutBtn.disabled = false;
            checkoutBtn.textContent = 'Оформить заказ';
        }
    }
}

// Функция для загрузки корзины
async function loadCart() {
    hideError();
    
    try {
        const cartData = await calculateCartTotal();
        renderCartItems(cartData.items);
        updateTotalPrice(cartData.total);
        
        // Показываем уведомление о режиме работы
        if (cartData.items.length > 0) {
            console.log('Корзина загружена успешно');
        }
    } catch (error) {
        console.error('Ошибка при загрузке корзины:', error);
        showError('Не удалось загрузить корзину. Проверьте подключение к серверу.');
        
        // Показываем пустую корзину в случае ошибки
        const cartItemsContainer = document.getElementById('cart-items');
        if (cartItemsContainer) {
            cartItemsContainer.innerHTML = `
                <div class="empty-cart">
                    <h2>Ошибка загрузки</h2>
                    <p>Не удалось загрузить содержимое корзины</p>
                    <button onclick="loadCart()" style="background-color: #FF9900; color: #0F1014; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer;">Попробовать снова</button>
                </div>
            `;
        }
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Мигрируем данные корзины при загрузке
    migrateCartData();
    
    // Очищаем некорректные записи
    cleanCartData();
    
    // Загружаем корзину
    loadCart();
    
    // Обновляем счетчик корзины
    updateCartCount();
    
    // Обработчик для кнопки оформления заказа
    const checkoutBtn = document.getElementById('checkout-btn');
    if (checkoutBtn) {
        checkoutBtn.addEventListener('click', createOrder);
    }
    
    // Обработчик для кнопки очистки корзины
    const clearCartBtn = document.getElementById('clear-cart-btn');
    if (clearCartBtn) {
        clearCartBtn.addEventListener('click', function() {
            if (confirm('Вы уверены, что хотите очистить корзину?')) {
                clearCart();
                loadCart();
            }
        });
    }
    
    // Обработчик для кнопки выхода (если есть)
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function() {
            localStorage.removeItem('accessToken');
            alert('Вы вышли из системы.');
            window.location.href = 'index.html';
        });
    }
    
    // Проверяем авторизацию пользователя
    const loginLink = document.getElementById('login-link');
    const userProfileBlock = document.getElementById('user-profile-block');
    const accessToken = localStorage.getItem('accessToken');

    if (accessToken) {
        // Пользователь авторизован
        if(loginLink) loginLink.style.display = 'none';
        if(userProfileBlock) userProfileBlock.style.display = 'flex';
    } else {
        // Пользователь не авторизован
        if(loginLink) loginLink.style.display = 'block';
        if(userProfileBlock) userProfileBlock.style.display = 'none';
    }
    
    // Настраиваем поиск в корзине
    setupCartSearch();
});

// ===== ПОИСК В КОРЗИНЕ =====

// Переменные для поиска в корзине
let cartSearchFilters = {
    search: '',
    genre: '',
    author: ''
};

// Настройка поиска в корзине
function setupCartSearch() {
    // Обработчик для кнопки поиска в хедере
    const headerSearchBtn = document.getElementById('header-search-btn');
    if (headerSearchBtn) {
        headerSearchBtn.addEventListener('click', handleCartHeaderSearchClick);
    }
    
    // Обработчики для выпадающего поиска
    setupCartDropdownSearchHandlers();
}

// Обработка клика по кнопке поиска в хедере корзины
function handleCartHeaderSearchClick() {
    const dropdown = document.getElementById('search-dropdown-content');
    
    if (dropdown) {
        // Показываем/скрываем выпадающий поиск
        toggleCartSearchDropdown();
    }
}

// Показать/скрыть выпадающий поиск в корзине
function toggleCartSearchDropdown() {
    const dropdown = document.getElementById('search-dropdown-content');
    if (dropdown) {
        dropdown.classList.toggle('show');
        
        if (dropdown.classList.contains('show')) {
            // Фокусируемся на поле поиска при открытии
            const dropdownInput = document.getElementById('dropdown-search-input');
            if (dropdownInput) {
                setTimeout(() => dropdownInput.focus(), 100);
            }
            
            // Заполняем фильтры данными из корзины
            populateCartDropdownFilters();
        }
    }
}

// Заполнение фильтров в выпадающем поиске корзины
function populateCartDropdownFilters() {
    const genreFilter = document.getElementById('dropdown-genre-filter');
    const authorFilter = document.getElementById('dropdown-author-filter');
    
    if (genreFilter) {
        // Получаем уникальные жанры из товаров в корзине
        const cartWithQuantity = getCartWithQuantity();
        const productIds = Object.keys(cartWithQuantity);
        const genres = new Set();
        
        // Добавляем жанры из моковых данных
        productIds.forEach(id => {
            if (MOCK_PRODUCTS[id] && MOCK_PRODUCTS[id].genre) {
                genres.add(MOCK_PRODUCTS[id].genre);
            }
        });
        
        const currentGenreValue = genreFilter.value;
        genreFilter.innerHTML = '<option value="">Все жанры</option>';
        
        const genreMap = {
            'fiction': 'Художественная литература',
            'psychology': 'Психология',
            'business': 'Бизнес',
            'history': 'История',
            'science': 'Наука',
            'rock': 'Рок',
            'classic-rock': 'Классический рок',
            'pop': 'Поп',
            'jazz': 'Джаз',
            'classical': 'Классическая музыка',
            'progressive': 'Прогрессив рок',
            'heavy-metal': 'Хеви-метал',
            'punk': 'Панк',
            'blues': 'Блюз',
            'reggae': 'Регги',
            'folk': 'Фолк',
            'soviet-rock': 'Советский рок',
            'soul': 'Соул',
            'funk': 'Фанк',
            'disco': 'Диско',
            'alternative': 'Альтернативный рок',
            'indie': 'Инди',
            'electronic': 'Электронная музыка',
            'country': 'Кантри'
        };
        
        genres.forEach(genre => {
            const option = document.createElement('option');
            option.value = genre;
            option.textContent = genreMap[genre] || genre;
            genreFilter.appendChild(option);
        });
        
        if (currentGenreValue) {
            genreFilter.value = currentGenreValue;
        }
    }
    
    if (authorFilter) {
        // Получаем уникальных авторов из товаров в корзине
        const cartWithQuantity = getCartWithQuantity();
        const productIds = Object.keys(cartWithQuantity);
        const authors = new Set();
        
        // Добавляем авторов из моковых данных
        productIds.forEach(id => {
            if (MOCK_PRODUCTS[id] && MOCK_PRODUCTS[id].author) {
                authors.add(MOCK_PRODUCTS[id].author);
            }
        });
        
        const currentAuthorValue = authorFilter.value;
        authorFilter.innerHTML = '<option value="">Все авторы</option>';
        
        authors.forEach(author => {
            const option = document.createElement('option');
            option.value = author;
            option.textContent = author;
            authorFilter.appendChild(option);
        });
        
        if (currentAuthorValue) {
            authorFilter.value = currentAuthorValue;
        }
    }
}

// Настройка обработчиков для выпадающего поиска в корзине
function setupCartDropdownSearchHandlers() {
    // Кнопка закрытия выпадающего поиска
    const closeBtn = document.getElementById('search-dropdown-close');
    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            const dropdown = document.getElementById('search-dropdown-content');
            if (dropdown) {
                dropdown.classList.remove('show');
            }
        });
    }
    
    // Кнопка поиска в выпадающем меню
    const searchBtn = document.getElementById('dropdown-search-btn');
    if (searchBtn) {
        searchBtn.addEventListener('click', handleCartDropdownSearch);
    }
    
    // Кнопка очистки в выпадающем меню
    const clearBtn = document.getElementById('dropdown-clear-btn');
    if (clearBtn) {
        clearBtn.addEventListener('click', handleCartDropdownClear);
    }
    
    // Обработчик Enter в поле поиска выпадающего меню
    const dropdownInput = document.getElementById('dropdown-search-input');
    if (dropdownInput) {
        dropdownInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                handleCartDropdownSearch();
            }
        });
    }
    
    // Обработчики изменения фильтров в выпадающем меню
    const genreFilter = document.getElementById('dropdown-genre-filter');
    const authorFilter = document.getElementById('dropdown-author-filter');
    
    if (genreFilter) {
        genreFilter.addEventListener('change', handleCartDropdownFilterChange);
    }
    
    if (authorFilter) {
        authorFilter.addEventListener('change', handleCartDropdownFilterChange);
    }
    
    // Закрытие выпадающего поиска при клике вне его
    document.addEventListener('click', function(event) {
        const dropdown = document.getElementById('search-dropdown-content');
        const searchBtn = document.getElementById('header-search-btn');
        
        if (dropdown && searchBtn && 
            !dropdown.contains(event.target) && 
            !searchBtn.contains(event.target)) {
            dropdown.classList.remove('show');
        }
    });
}

// Обработка поиска в выпадающем меню корзины
function handleCartDropdownSearch() {
    const dropdownInput = document.getElementById('dropdown-search-input');
    const genreFilter = document.getElementById('dropdown-genre-filter');
    const authorFilter = document.getElementById('dropdown-author-filter');
    
    if (dropdownInput) {
        const searchTerm = dropdownInput.value.trim().toLowerCase();
        const genre = genreFilter ? genreFilter.value : '';
        const author = authorFilter ? authorFilter.value : '';
        
        // Обновляем фильтры поиска
        cartSearchFilters.search = searchTerm;
        cartSearchFilters.genre = genre;
        cartSearchFilters.author = author;
        
        // Выполняем поиск в корзине
        filterCartItems();
        
        // Закрываем выпадающий поиск
        const dropdown = document.getElementById('search-dropdown-content');
        if (dropdown) {
            dropdown.classList.remove('show');
        }
    }
}

// Обработка очистки в выпадающем меню корзины
function handleCartDropdownClear() {
    const dropdownInput = document.getElementById('dropdown-search-input');
    const genreFilter = document.getElementById('dropdown-genre-filter');
    const authorFilter = document.getElementById('dropdown-author-filter');
    
    if (dropdownInput) dropdownInput.value = '';
    if (genreFilter) genreFilter.value = '';
    if (authorFilter) authorFilter.value = '';
    
    // Очищаем фильтры поиска
    cartSearchFilters.search = '';
    cartSearchFilters.genre = '';
    cartSearchFilters.author = '';
    
    // Показываем все товары в корзине
    filterCartItems();
}

// Обработка изменения фильтров в выпадающем меню корзины
function handleCartDropdownFilterChange(event) {
    const filterType = event.target.id.replace('dropdown-', '').replace('-filter', '');
    cartSearchFilters[filterType] = event.target.value;
}

// Фильтрация товаров в корзине
function filterCartItems() {
    const cartItems = document.querySelectorAll('.cart-item');
    
    cartItems.forEach(item => {
        const title = item.querySelector('.cart-item-title').textContent.toLowerCase();
        const author = item.querySelector('.cart-item-author').textContent.toLowerCase();
        const productId = item.getAttribute('data-product-id');
        
        let showItem = true;
        
        // Фильтр по поисковому запросу
        if (cartSearchFilters.search) {
            showItem = showItem && (
                title.includes(cartSearchFilters.search) ||
                author.includes(cartSearchFilters.search)
            );
        }
        
        // Фильтр по жанру (если есть данные о жанре)
        if (cartSearchFilters.genre && MOCK_PRODUCTS[productId]) {
            const productGenre = MOCK_PRODUCTS[productId].genre;
            showItem = showItem && productGenre === cartSearchFilters.genre;
        }
        
        // Фильтр по автору
        if (cartSearchFilters.author) {
            showItem = showItem && author.includes(cartSearchFilters.author.toLowerCase());
        }
        
        // Показываем или скрываем товар
        item.style.display = showItem ? 'flex' : 'none';
    });
    
    // Показываем сообщение, если ничего не найдено
    showCartSearchResults();
}

// Показ результатов поиска в корзине
function showCartSearchResults() {
    const cartItems = document.querySelectorAll('.cart-item');
    const visibleItems = Array.from(cartItems).filter(item => item.style.display !== 'none');
    
    // Удаляем предыдущее сообщение о результатах поиска
    const existingMessage = document.getElementById('cart-search-results');
    if (existingMessage) {
        existingMessage.remove();
    }
    
    // Если есть активные фильтры и найдены результаты
    if ((cartSearchFilters.search || cartSearchFilters.genre || cartSearchFilters.author) && visibleItems.length > 0) {
        const cartItemsContainer = document.getElementById('cart-items');
        const searchMessage = document.createElement('div');
        searchMessage.id = 'cart-search-results';
        searchMessage.className = 'cart-search-results';
        searchMessage.innerHTML = `
            <div class="search-results-info">
                <span class="search-icon">🔍</span>
                <span class="search-text">Найдено товаров: <strong>${visibleItems.length}</strong></span>
                <button class="clear-search-btn" onclick="clearCartSearch()">✕</button>
            </div>
        `;
        
        // Вставляем перед товарами
        cartItemsContainer.insertBefore(searchMessage, cartItemsContainer.firstChild);
    }
    
    // Если ничего не найдено
    if ((cartSearchFilters.search || cartSearchFilters.genre || cartSearchFilters.author) && visibleItems.length === 0) {
        const cartItemsContainer = document.getElementById('cart-items');
        const noResultsMessage = document.createElement('div');
        noResultsMessage.id = 'cart-search-results';
        noResultsMessage.className = 'cart-no-results';
        noResultsMessage.innerHTML = `
            <div class="no-results-info">
                <span class="search-icon">🔍</span>
                <span class="no-results-text">По вашему запросу ничего не найдено в корзине</span>
                <button class="clear-search-btn" onclick="clearCartSearch()">✕</button>
            </div>
        `;
        
        // Вставляем перед товарами
        cartItemsContainer.insertBefore(noResultsMessage, cartItemsContainer.firstChild);
    }
}

// Очистка поиска в корзине
function clearCartSearch() {
    // Очищаем фильтры
    cartSearchFilters.search = '';
    cartSearchFilters.genre = '';
    cartSearchFilters.author = '';
    
    // Очищаем поля в выпадающем меню
    const dropdownInput = document.getElementById('dropdown-search-input');
    const genreFilter = document.getElementById('dropdown-genre-filter');
    const authorFilter = document.getElementById('dropdown-author-filter');
    
    if (dropdownInput) dropdownInput.value = '';
    if (genreFilter) genreFilter.value = '';
    if (authorFilter) authorFilter.value = '';
    
    // Показываем все товары
    const cartItems = document.querySelectorAll('.cart-item');
    cartItems.forEach(item => {
        item.style.display = 'flex';
    });
    
    // Удаляем сообщение о результатах поиска
    const searchMessage = document.getElementById('cart-search-results');
    if (searchMessage) {
        searchMessage.remove();
    }
}

// Экспортируем функции в глобальную область видимости
window.clearCartSearch = clearCartSearch;
