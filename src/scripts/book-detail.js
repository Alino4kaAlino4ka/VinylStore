// Код для страницы детальной информации о пластинке (book-detail.html)

// API конфигурация (унифицирована с другими скриптами)
const API_BASE_URL = window.API_CONFIG?.catalog || 'http://localhost:8000';
const PRODUCTS_ENDPOINT = `${API_BASE_URL}/api/v1/products`;

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', async function() {
    // Получаем ID пластинки из параметров URL
    const urlParams = new URLSearchParams(window.location.search);
    const recordId = urlParams.get('id');
    
    if (!recordId) {
        console.error('ID пластинки не указан в URL параметрах');
        showError('ID пластинки не указан. Используйте формат: ?id=1');
        return;
    }
    
    // Индикатор загрузки уже виден в HTML
    // Загружаем данные пластинки
    await loadRecordDetails(recordId);
});

// Загрузка детальной информации о пластинке
async function loadRecordDetails(recordId) {
    try {
        const response = await fetch(`${PRODUCTS_ENDPOINT}/${recordId}`);
        
        if (!response.ok) {
            if (response.status === 404) {
                throw new Error('Пластинка не найдена');
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const recordData = await response.json();
        
        // Очищаем содержимое main элемента (включая индикатор загрузки)
        const mainElement = document.querySelector('main.page-content');
        if (mainElement) {
            mainElement.innerHTML = '';
        }
        
        // Создаем и добавляем карточку виниловой пластинки
        // Передаем и recordData и recordId для правильной работы
        const bookCard = createBookDetailCard(recordData, recordId);
        if (mainElement && bookCard) {
            mainElement.appendChild(bookCard);
        }
        
    } catch (error) {
        console.error('Ошибка загрузки деталей пластинки:', error);
        showError(`Не удалось загрузить информацию о пластинке: ${error.message}`);
    }
}

// Создание детальной карточки виниловой пластинки
function createBookDetailCard(recordData, urlBookId = null) {
    // Извлекаем данные из ответа API
    // API возвращает: name, artist (строка), description, price, cover_url
    const title = recordData.name || recordData.title || 'Название не указано';
    const artistName = typeof recordData.artist === 'string' ? recordData.artist : (recordData.artist?.name || (typeof recordData.author === 'string' ? recordData.author : (recordData.author?.name || 'Исполнитель не указан')));
    const description = recordData.description || 'Описание отсутствует';
    const coverUrl = recordData.cover_url || recordData.cover_image_url || null;
    const price = recordData.price || 0;
    // ВАЖНО: Используем ID из данных API, это гарантирует правильность
    const recordId = recordData.id || urlBookId;
    const rating = recordData.rating || (Math.random() * 2 + 3).toFixed(1); // Генерируем рейтинг если нет в API
    const ratingCount = recordData.rating_count || Math.floor(Math.random() * 50000 + 1000);
    
    // Обновляем title страницы
    document.title = `${title} - Винил Шоп`;
    
    // Создаем основной контейнер секции
    const section = document.createElement('section');
    section.className = 'book-details';
    
    // Секция с обложкой (левая колонка)
    const coverSection = document.createElement('div');
    coverSection.className = 'book-cover-section';
    
    // Контейнер обложки
    const coverContainer = document.createElement('div');
    coverContainer.className = 'cover-container';
    
    // Изображение обложки с overlay
    const coverImageDiv = document.createElement('div');
    coverImageDiv.className = 'book-cover-image';
    
    // SVG placeholder для виниловой пластинки (работает без интернета)
    const VINYL_PLACEHOLDER_SVG = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='600' height='600'%3E%3Crect fill='%238A2BE2' width='600' height='600'/%3E%3Ctext x='50%25' y='45%25' dominant-baseline='middle' text-anchor='middle' font-family='Arial' font-size='24' fill='white'%3EVinyl Record%3C/text%3E%3Ctext x='50%25' y='55%25' dominant-baseline='middle' text-anchor='middle' font-family='Arial' font-size='18' fill='white' opacity='0.8'%3E💿%3C/text%3E%3C/svg%3E";
    
    const safeCoverUrl = coverUrl && coverUrl !== 'null' && coverUrl !== 'undefined' ? coverUrl : VINYL_PLACEHOLDER_SVG;
    
    const coverImg = document.createElement('img');
    coverImg.src = safeCoverUrl;
    coverImg.alt = `Обложка пластинки ${title}`;
    coverImg.onerror = function() {
        this.onerror = null;
        this.src = VINYL_PLACEHOLDER_SVG;
    };
    
    const playOverlay = document.createElement('div');
    playOverlay.className = 'play-overlay';
    const playOverlayBtn = document.createElement('button');
    playOverlayBtn.className = 'play-overlay-btn';
    playOverlayBtn.textContent = '▶';
    playOverlay.appendChild(playOverlayBtn);
    
    coverImageDiv.appendChild(coverImg);
    coverImageDiv.appendChild(playOverlay);
    
    const storeName = document.createElement('div');
    storeName.className = 'store-name';
    storeName.textContent = 'Винил Шоп';
    
    coverContainer.appendChild(coverImageDiv);
    coverContainer.appendChild(storeName);
    
    // Плеер
    const audioPlayer = document.createElement('div');
    audioPlayer.className = 'audio-player';
    
    const playerLabel = document.createElement('span');
    playerLabel.className = 'player-label';
    playerLabel.textContent = 'Слушать фрагмент';
    
    const playerControls = document.createElement('div');
    playerControls.className = 'player-controls';
    
    const rewindBtn = document.createElement('button');
    rewindBtn.className = 'player-btn skip-btn';
    rewindBtn.title = 'Назад 15 сек';
    rewindBtn.innerHTML = '⟲ <span>15</span>';
    
    const playBtn = document.createElement('button');
    playBtn.className = 'player-btn play-btn-large';
    playBtn.textContent = '▶';
    
    const forwardBtn = document.createElement('button');
    forwardBtn.className = 'player-btn skip-btn';
    forwardBtn.title = 'Вперед 15 сек';
    forwardBtn.innerHTML = '⟳ <span>15</span>';
    
    const repeatBtn = document.createElement('button');
    repeatBtn.className = 'player-btn repeat-btn';
    repeatBtn.title = 'Повтор';
    repeatBtn.textContent = '↻';
    
    playerControls.appendChild(rewindBtn);
    playerControls.appendChild(playBtn);
    playerControls.appendChild(forwardBtn);
    playerControls.appendChild(repeatBtn);
    
    const buyBtnLarge = document.createElement('button');
    buyBtnLarge.className = 'buy-btn-large';
    // ВАЖНО: Используем ID из данных API, это гарантирует правильность
    // recordId здесь уже правильно определен (из recordData.id || urlBookId)
    buyBtnLarge.setAttribute('data-product-id', recordId);
    buyBtnLarge.setAttribute('data-book-id', recordId);
    buyBtnLarge.textContent = 'В корзину';
    
    // Обработчик клика для добавления в корзину
    buyBtnLarge.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation(); // Предотвращаем всплытие к другим обработчикам
        // Используем recordId, который уже содержит правильный ID из данных API
        console.log('Клик по кнопке "В корзину" на странице детализации:');
        console.log('- recordData.id:', recordData.id);
        console.log('- recordId (используется):', recordId);
        addToCartFromDetail(recordId, recordData);
    });
    
    audioPlayer.appendChild(playerLabel);
    audioPlayer.appendChild(playerControls);
    audioPlayer.appendChild(buyBtnLarge);
    
    coverSection.appendChild(coverContainer);
    coverSection.appendChild(audioPlayer);
    
    // Секция с информацией о пластинке (правая колонка)
    const infoSection = document.createElement('div');
    infoSection.className = 'book-info-section';
    
    // Секция заголовка
    const titleSection = document.createElement('div');
    titleSection.className = 'title-section';
    
    const h1 = document.createElement('h1');
    h1.textContent = title;
    
    const titleActions = document.createElement('div');
    titleActions.className = 'title-actions';
    
    const ageRating = document.createElement('span');
    ageRating.className = 'age-rating';
    ageRating.textContent = '18+';
    
    const bookmarkIcon = document.createElement('span');
    bookmarkIcon.className = 'bookmark-icon';
    bookmarkIcon.textContent = '🔖';
    
    titleActions.appendChild(ageRating);
    titleActions.appendChild(bookmarkIcon);
    
    titleSection.appendChild(h1);
    titleSection.appendChild(titleActions);
    
    // Мета-информация
    const metaInfo = document.createElement('div');
    metaInfo.className = 'meta-info';
    
    const artistSpan = document.createElement('span');
    const artistLink = document.createElement('a');
    artistLink.href = '#';
    artistLink.textContent = artistName;
    artistSpan.textContent = 'Исполнитель: ';
    artistSpan.appendChild(artistLink);
    
    // narratorSpan убран для виниловых пластинок (нет чтеца)
    
    metaInfo.appendChild(artistSpan);
    
    // Секция рейтинга
    const ratingSection = document.createElement('div');
    ratingSection.className = 'rating-section';
    
    const ratingScore = document.createElement('span');
    ratingScore.className = 'rating-score';
    ratingScore.textContent = rating;
    
    const ratingText = document.createElement('span');
    ratingText.className = 'rating-text';
    ratingText.innerHTML = `Рейтинг аудитории<br>${ratingCount.toLocaleString('ru-RU')} оценок`;
    
    ratingSection.appendChild(ratingScore);
    ratingSection.appendChild(ratingText);
    
    // Описание
    const descriptionP = document.createElement('p');
    descriptionP.className = 'description';
    const isLongDescription = description.length > 500;
    const shortDescription = isLongDescription ? description.substring(0, 500) + '...' : description;
    
    if (isLongDescription) {
        descriptionP.innerHTML = `${shortDescription} <a href="#" class="expand-link">развернуть ▾</a>`;
        
        // Сохраняем полное описание в data-атрибуте
        descriptionP.setAttribute('data-full-description', description);
        descriptionP.setAttribute('data-short-description', shortDescription);
        descriptionP.setAttribute('data-expanded', 'false');
        
        // Добавляем обработчик клика на ссылку "развернуть"
        descriptionP.addEventListener('click', function(e) {
            if (e.target.classList.contains('expand-link')) {
                e.preventDefault();
                const isExpanded = descriptionP.getAttribute('data-expanded') === 'true';
                
                if (isExpanded) {
                    // Сворачиваем описание
                    const shortDesc = descriptionP.getAttribute('data-short-description');
                    descriptionP.innerHTML = `${shortDesc} <a href="#" class="expand-link">развернуть ▾</a>`;
                    descriptionP.setAttribute('data-expanded', 'false');
                } else {
                    // Разворачиваем описание
                    const fullDesc = descriptionP.getAttribute('data-full-description');
                    descriptionP.innerHTML = `${fullDesc} <a href="#" class="expand-link">свернуть ▲</a>`;
                    descriptionP.setAttribute('data-expanded', 'true');
                }
            }
        });
    } else {
        descriptionP.textContent = description;
    }
    
    // Социальные ссылки
    const socialLinks = document.createElement('div');
    socialLinks.className = 'social-links';
    socialLinks.innerHTML = '<a href="#">VK</a> <a href="#">IG</a> <a href="#">FB</a> <a href="#">YT</a>';
    
    // Собираем секцию информации
    infoSection.appendChild(titleSection);
    infoSection.appendChild(metaInfo);
    infoSection.appendChild(ratingSection);
    infoSection.appendChild(descriptionP);
    infoSection.appendChild(socialLinks);
    
    // Собираем основную секцию
    section.appendChild(coverSection);
    section.appendChild(infoSection);
    
    return section;
}

// Добавление в корзину со страницы детализации
function addToCartFromDetail(recordId, recordData) {
    // ВАЖНО: Используем ID из данных API, а не из URL параметра
    // Это гарантирует, что добавляется правильная пластинка
    const actualBookId = recordData.id || recordId;
    const normalizedId = String(actualBookId);
    
    console.log('addToCartFromDetail вызвана:');
    console.log('- ID из URL:', recordId);
    console.log('- ID из API данных:', recordData.id);
    console.log('- Используемый ID:', normalizedId);
    
    const title = recordData.name || recordData.title || 'Пластинка';
    
    // Сохраняем информацию о товаре в localStorage для использования в корзине
    const productInfo = {
        id: actualBookId,
        title: title,
        price: recordData.price || 0,
        image_url: recordData.cover_url || recordData.cover_image_url || '',
        artist: typeof recordData.artist === 'string' ? recordData.artist : (recordData.artist?.name || 'Неизвестный исполнитель'),
        description: recordData.description || ''
    };
    
    // Сохраняем информацию о товаре отдельно
    let productsInfo = {};
    try {
        const stored = localStorage.getItem('productsInfo');
        if (stored) {
            productsInfo = JSON.parse(stored);
        }
    } catch (e) {
        console.warn('Ошибка при чтении productsInfo:', e);
    }
    productsInfo[normalizedId] = productInfo;
    localStorage.setItem('productsInfo', JSON.stringify(productsInfo));
    
    // Используем новую систему корзины с количеством
    if (typeof window.addToCartWithQuantity === 'function') {
        window.addToCartWithQuantity(normalizedId);
    } else {
        // Fallback на старую систему
        let cart = JSON.parse(localStorage.getItem('cart') || '[]');
        const existingItem = cart.find(item => String(item.id) === normalizedId);
        
        if (existingItem) {
            existingItem.quantity += 1;
        } else {
            cart.push({
                id: actualBookId,
                title: title,
                price: recordData.price || 0,
                image: recordData.cover_url || recordData.cover_image_url || '',
                quantity: 1
            });
        }
        
        localStorage.setItem('cart', JSON.stringify(cart));
    }
    
    // Обновляем счетчик корзины
    updateCartCount();
    
    // Показываем уведомление
    showNotification(`"${title}" добавлена в корзину!`);
}

// Обновление счетчика корзины
function updateCartCount() {
    if (typeof window.getCartWithQuantity === 'function') {
        const cartWithQuantity = window.getCartWithQuantity();
        const totalItems = Object.values(cartWithQuantity).reduce((sum, quantity) => sum + quantity, 0);
        const cartCountElement = document.getElementById('cart-count');
        if (cartCountElement) {
            cartCountElement.textContent = totalItems;
        }
    } else if (typeof window.updateCartCount === 'function') {
        window.updateCartCount();
    } else {
        // Fallback на старую систему
        const cart = JSON.parse(localStorage.getItem('cart') || '[]');
        const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
        const cartCountElement = document.getElementById('cart-count');
        if (cartCountElement) {
            cartCountElement.textContent = totalItems;
        }
    }
}

// Показ уведомления
function showNotification(message) {
    // Проверяем, есть ли уже уведомление, чтобы не дублировать
    const existingNotification = document.querySelector('.notification-book-detail');
    if (existingNotification) {
        existingNotification.remove();
    }
    
    // Создаем элемент уведомления
    const notification = document.createElement('div');
    notification.className = 'notification notification-book-detail';
    notification.textContent = message;
    
    // Добавляем стили
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background-color: #FF9900;
        color: #0F1014;
        padding: 15px 20px;
        border-radius: 8px;
        font-weight: bold;
        z-index: 10000;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        animation: slideInNotification 0.3s ease-out;
    `;
    
    // Добавляем анимацию, если её ещё нет
    if (!document.getElementById('notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            @keyframes slideInNotification {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOutNotification {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }
    
    // Добавляем на страницу
    document.body.appendChild(notification);
    
    // Удаляем через 3 секунды
    setTimeout(() => {
        notification.style.animation = 'slideOutNotification 0.3s ease-out';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// Функция для отображения ошибки
function showError(message) {
    const mainElement = document.querySelector('main.page-content');
    if (mainElement) {
        mainElement.innerHTML = `
            <div style="padding: 40px; text-align: center;">
                <h2 style="color: #d32f2f;">Ошибка</h2>
                <p style="color: #666; margin-top: 20px;">${message}</p>
            </div>
        `;
    }
}

