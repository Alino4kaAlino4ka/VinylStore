// Функции для работы с корзиной
function getCart() {
    const cart = localStorage.getItem('cart');
    return cart ? JSON.parse(cart) : [];
}

function saveCart(cart) {
    localStorage.setItem('cart', JSON.stringify(cart));
}

function updateCartCount() {
    // Проверяем, есть ли новая система корзины
    if (typeof window.getCartWithQuantity === 'function') {
        // Вызываем миграцию перед обновлением счетчика
        if (typeof window.migrateCartData === 'function') {
            window.migrateCartData();
        }
        
        const cartWithQuantity = window.getCartWithQuantity();
        const totalItems = Object.values(cartWithQuantity).reduce((sum, quantity) => sum + quantity, 0);
        const cartCountElement = document.getElementById('cart-count');
        if (cartCountElement) {
            cartCountElement.textContent = totalItems;
        }
    } else {
        // Fallback для старой системы
        const cart = getCart();
        const cartCountElement = document.getElementById('cart-count');
        if (cartCountElement) {
            cartCountElement.textContent = cart.length;
        }
    }
}

function addToCart(productId) {
    // Проверяем, есть ли функция addToCart в cart.js (проверяем по другому имени)
    if (typeof window.addToCartWithQuantity === 'function') {
        window.addToCartWithQuantity(productId);
    } else {
        // Fallback для старой системы
        const cart = getCart();
        
        // Проверяем, есть ли уже этот товар в корзине
        if (!cart.includes(productId)) {
            cart.push(productId);
            saveCart(cart);
            updateCartCount();
            
            // Показываем уведомление пользователю
            const button = document.querySelector(`[data-product-id="${productId}"] .add-to-cart-btn, .add-to-cart-btn[data-product-id="${productId}"]`);
            if (button) {
                const originalText = button.textContent;
                button.textContent = 'Добавлено!';
                button.style.backgroundColor = '#28a745';
                
                setTimeout(() => {
                    button.textContent = originalText;
                    button.style.backgroundColor = '';
                }, 2000);
            }
        } else {
            alert('Этот товар уже в корзине!');
        }
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Обработчики для кнопок покупки (теперь они добавляют в корзину)
    // НЕ обрабатываем buy-btn-large, так как у них есть свои обработчики
    const buyButtons = document.querySelectorAll('.buy-btn:not(.buy-btn-large)');
    buyButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation(); // Предотвращаем всплытие
            const productId = this.getAttribute('data-product-id');
            if (productId) {
                addToCart(productId);
            }
        });
    });

    const loginLink = document.getElementById('login-link');
    const userProfileBlock = document.getElementById('user-profile-block');
    const logoutBtn = document.getElementById('logout-btn');

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

    if (logoutBtn) {
        logoutBtn.addEventListener('click', function() {
            localStorage.removeItem('accessToken');
            alert('Вы вышли из системы.');
            window.location.reload(); // Перезагружаем страницу для обновления UI
        });
    }

    // Обновляем счетчик корзины при загрузке страницы
    updateCartCount();

    // Обработчик для кнопок добавления в корзину (делегирование событий)
    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('add-to-cart-btn')) {
            // Сначала проверяем, есть ли data-product-id у самой кнопки
            let productId = event.target.getAttribute('data-product-id');
            
            // Если у кнопки нет data-product-id, ищем в родительском элементе
            if (!productId) {
                const productCard = event.target.closest('[data-product-id]');
                if (productCard) {
                    productId = productCard.getAttribute('data-product-id');
                }
            }
            
            if (productId) {
                addToCart(productId);
            }
        }
    });

    // Обработчик для кнопки поиска в хедере (только если catalog.js не загружен)
    const headerSearchBtn = document.getElementById('header-search-btn');
    if (headerSearchBtn && typeof handleHeaderSearchClick === 'undefined' && typeof toggleSearchDropdown === 'undefined') {
        headerSearchBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            const dropdown = document.getElementById('search-dropdown-content');
            if (dropdown) {
                dropdown.classList.toggle('show');
                
                if (dropdown.classList.contains('show')) {
                    // Фокусируемся на поле поиска при открытии
                    const dropdownInput = document.getElementById('dropdown-search-input');
                    if (dropdownInput) {
                        setTimeout(() => dropdownInput.focus(), 100);
                    }
                }
            }
        });
    }

    // Обработчик для кнопки закрытия выпадающего поиска
    const closeSearchBtn = document.getElementById('search-dropdown-close');
    if (closeSearchBtn) {
        closeSearchBtn.addEventListener('click', function() {
            const dropdown = document.getElementById('search-dropdown-content');
            if (dropdown) {
                dropdown.classList.remove('show');
            }
        });
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

    // Обработчик для кнопки поиска в выпадающем меню (если catalog.js не загружен)
    const dropdownSearchBtn = document.getElementById('dropdown-search-btn');
    if (dropdownSearchBtn && typeof handleDropdownSearch === 'undefined') {
        dropdownSearchBtn.addEventListener('click', function() {
            const dropdownInput = document.getElementById('dropdown-search-input');
            const genreFilter = document.getElementById('dropdown-genre-filter');
            const artistFilter = document.getElementById('dropdown-author-filter');
            
            if (dropdownInput) {
                const searchTerm = dropdownInput.value.trim();
                const genre = genreFilter ? genreFilter.value : '';
                const artist = artistFilter ? artistFilter.value : '';
                
                // Формируем URL с параметрами поиска
                const searchParams = new URLSearchParams();
                if (searchTerm) searchParams.set('q', searchTerm);
                if (genre) searchParams.set('genre', genre);
                if (artist) searchParams.set('artist', artist);
                const queryString = searchParams.toString();
                
                // Переходим на страницу поиска
                window.location.href = 'search.html' + (queryString ? '?' + queryString : '');
            }
        });
    }

    // Обработчик Enter в поле поиска выпадающего меню
    const dropdownInput = document.getElementById('dropdown-search-input');
    if (dropdownInput && typeof handleDropdownSearch === 'undefined') {
        dropdownInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                const searchBtn = document.getElementById('dropdown-search-btn');
                if (searchBtn) {
                    searchBtn.click();
                }
            }
        });
    }
});
