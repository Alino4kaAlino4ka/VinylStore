// Каталог виниловых пластинок - JavaScript функциональность

// API конфигурация (унифицирована с другими скриптами)
const API_BASE_URL = window.API_CONFIG?.catalog || 'http://localhost:8000';
const PRODUCTS_ENDPOINT = `${API_BASE_URL}/api/v1/products`;

// SVG placeholder для виниловой пластинки (работает без интернета)
const VINYL_PLACEHOLDER_SVG = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='600' height='600'%3E%3Crect fill='%238A2BE2' width='600' height='600'/%3E%3Ctext x='50%25' y='45%25' dominant-baseline='middle' text-anchor='middle' font-family='Arial' font-size='24' fill='white'%3EVinyl Record%3C/text%3E%3Ctext x='50%25' y='55%25' dominant-baseline='middle' text-anchor='middle' font-family='Arial' font-size='18' fill='white' opacity='0.8'%3E💿%3C/text%3E%3C/svg%3E";

// Данные виниловых пластинок (загружаются с сервера)
let vinylRecords = [];

// Экспортируем vinylRecords в window для тестирования
window.vinylRecords = vinylRecords;

// Текущие фильтры
let currentFilters = {
    genre: '',
    artist: '',
    sort: 'popular',
    search: ''
};

// Текущая страница
let currentPage = 1;
const itemsPerPage = 6;

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', async function() {
    // Убеждаемся, что меню поиска закрыто при загрузке
    const dropdown = document.getElementById('search-dropdown-content');
    if (dropdown) {
        dropdown.classList.remove('show');
        console.log('Меню поиска закрыто при загрузке страницы');
    }
    
    await loadVinylRecords();
    setupEventListeners();
    loadCartCount();
    initializeCatalog();
});

// Загрузка виниловых пластинок с API
async function loadVinylRecords() {
    try {
        const response = await fetch(PRODUCTS_ENDPOINT);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        vinylRecords = data.products || [];
        
        // Синхронизируем с window для тестирования
        window.vinylRecords = vinylRecords;
        
        // Добавляем недостающие поля для совместимости
        vinylRecords = vinylRecords.map(record => ({
            ...record,
            title: record.name,
            artist: record.artist || record.author || 'Неизвестный исполнитель',
            author: record.artist || record.author || 'Неизвестный исполнитель', // Для обратной совместимости
            image: record.cover_url || null,
            rating: Math.random() * 2 + 3, // Генерируем случайный рейтинг от 3 до 5
            genre: getGenreFromTitle(record.name) // Определяем жанр по названию
        }));
        
        // Синхронизируем с window для тестирования
        window.vinylRecords = vinylRecords;
        
        populateFilters();
    } catch (error) {
        console.error('Ошибка загрузки виниловых пластинок:', error);
        showError('Не удалось загрузить каталог. Проверьте подключение к серверу.');
        // Не используем fallback с книгами - оставляем пустой массив
        vinylRecords = [];
        // Синхронизируем с window для тестирования
        window.vinylRecords = vinylRecords;
        populateFilters();
    }
}

// Определение жанра по названию пластинки
function getGenreFromTitle(title) {
    const titleLower = title.toLowerCase();
    
    // Хард-рок и хеви-метал
    if (titleLower.includes('sabbath') || titleLower.includes('metallica') || 
        titleLower.includes('iron maiden') || titleLower.includes('judas priest') ||
        titleLower.includes('heavy') || titleLower.includes('metal')) return 'heavy-metal';
    
    // Панк
    if (titleLower.includes('punk') || titleLower.includes('clash') || 
        titleLower.includes('sex pistols') || titleLower.includes('ramones')) return 'punk';
    
    // Прогрессив рок
    if (titleLower.includes('prog') || titleLower.includes('floyd') || 
        titleLower.includes('pink floyd') || titleLower.includes('genesis') ||
        titleLower.includes('yes') || titleLower.includes('king crimson')) return 'progressive';
    
    // Классический рок
    if (titleLower.includes('zeppelin') || titleLower.includes('stones') || 
        titleLower.includes('who') || titleLower.includes('deep purple') ||
        titleLower.includes('ac/dc') || titleLower.includes('hendrix')) return 'classic-rock';
    
    // Рок (общий)
    if (titleLower.includes('rock') || titleLower.includes('queen') || 
        titleLower.includes('bowie') || titleLower.includes('dylan')) return 'rock';
    
    // Поп
    if (titleLower.includes('pop') || titleLower.includes('beatles') || 
        titleLower.includes('michael jackson') || titleLower.includes('madonna')) return 'pop';
    
    // Джаз
    if (titleLower.includes('jazz') || titleLower.includes('miles davis') || 
        titleLower.includes('coltrane') || titleLower.includes('ellington')) return 'jazz';
    
    // Блюз
    if (titleLower.includes('blues') || titleLower.includes('bb king') || 
        titleLower.includes('muddy waters') || titleLower.includes('howlin wolf')) return 'blues';
    
    // Регги
    if (titleLower.includes('reggae') || titleLower.includes('bob marley') || 
        titleLower.includes('dub') || titleLower.includes('ska')) return 'reggae';
    
    // Фолк
    if (titleLower.includes('folk') || titleLower.includes('dylan')) return 'folk';
    
    // Классическая музыка
    if (titleLower.includes('классик') || titleLower.includes('rachmaninoff') || 
        titleLower.includes('рахманинов') || titleLower.includes('chopin') ||
        titleLower.includes('mozart') || titleLower.includes('beethoven') ||
        titleLower.includes('орган') || titleLower.includes('симфони')) return 'classical';
    
    // Советский рок
    if (titleLower.includes('кино') || titleLower.includes('аквариум') || 
        titleLower.includes('ддт') || titleLower.includes('наутилус') ||
        titleLower.includes('алиса') || titleLower.includes('земляне') ||
        titleLower.includes('машина времени') || titleLower.includes('сплин')) return 'soviet-rock';
    
    // Соул
    if (titleLower.includes('soul') || titleLower.includes('aretha') || 
        titleLower.includes('otis redding') || titleLower.includes('marvin gaye')) return 'soul';
    
    // Фанк
    if (titleLower.includes('funk') || titleLower.includes('james brown') || 
        titleLower.includes('parliament')) return 'funk';
    
    // Диско
    if (titleLower.includes('disco') || titleLower.includes('bee gees') || 
        titleLower.includes('abba')) return 'disco';
    
    // Альтернативный рок
    if (titleLower.includes('alternative') || titleLower.includes('nirvana') || 
        titleLower.includes('radiohead') || titleLower.includes('soundgarden')) return 'alternative';
    
    // Инди
    if (titleLower.includes('indie') || titleLower.includes('arcade fire') || 
        titleLower.includes('the strokes')) return 'indie';
    
    // Электронная музыка
    if (titleLower.includes('electronic') || titleLower.includes('kraftwerk') || 
        titleLower.includes('tangerine dream')) return 'electronic';
    
    // Кантри
    if (titleLower.includes('country') || titleLower.includes('johnny cash') || 
        titleLower.includes('willie nelson')) return 'country';
    
    return 'rock'; // По умолчанию рок
}

// Заглушка данных при недоступности API
function getFallbackData() {
    // Возвращаем пустой массив вместо старых книг
    return [];
}

// Заполнение фильтров уникальными значениями из данных
function populateFilters() {
    const genres = [...new Set(vinylRecords.map(record => record.genre))];
    const artists = [...new Set(vinylRecords.map(record => record.artist || record.author))];
    
    // Заполняем жанры
    const genreSelect = document.getElementById('genre-filter');
    const currentGenreValue = genreSelect.value;
    genreSelect.innerHTML = '<option value="">Все жанры</option>';
    
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
        genreSelect.appendChild(option);
    });
    
    // Восстанавливаем выбранное значение
    if (currentGenreValue) {
        genreSelect.value = currentGenreValue;
    }
    
    // Заполняем исполнителей
    const artistSelect = document.getElementById('author-filter') || document.getElementById('artist-filter');
    if (artistSelect) {
        const currentArtistValue = artistSelect.value;
        artistSelect.innerHTML = '<option value="">Все исполнители</option>';
        
        artists.forEach(artist => {
            const option = document.createElement('option');
            option.value = artist;
            option.textContent = artist;
            artistSelect.appendChild(option);
        });
        
        // Восстанавливаем выбранное значение
        if (currentArtistValue) {
            artistSelect.value = currentArtistValue;
        }
    }
}

// Показ ошибки
function showError(message) {
    const catalogGrid = document.getElementById('catalog-grid');
    catalogGrid.innerHTML = `
        <div class="error-message">
            <h3>Ошибка загрузки</h3>
            <p>${message}</p>
            <button onclick="location.reload()" class="retry-btn">Попробовать снова</button>
        </div>
    `;
}

// Инициализация каталога
function initializeCatalog() {
    // Показываем каталог и скрываем индикатор загрузки
    const catalogGrid = document.getElementById('catalog-grid');
    const loadingCatalog = document.getElementById('loading-catalog');
    
    if (catalogGrid) {
        catalogGrid.style.display = 'grid';
    }
    if (loadingCatalog) {
        loadingCatalog.style.display = 'none';
    }
    
    renderCatalog();
    renderPagination();
}

// Флаг для отслеживания клика по кнопке поиска (глобальный для всех обработчиков)
let isSearchButtonClicked = false;

// Настройка обработчиков событий
function setupEventListeners() {
    // Фильтры
    const genreFilter = document.getElementById('genre-filter');
    const artistFilter = document.getElementById('author-filter') || document.getElementById('artist-filter');
    const sortFilter = document.getElementById('sort-filter');
    
    if (genreFilter) genreFilter.addEventListener('change', handleFilterChange);
    if (artistFilter) artistFilter.addEventListener('change', handleFilterChange);
    if (sortFilter) sortFilter.addEventListener('change', handleFilterChange);
    
    // Сброс фильтров
    const resetFiltersBtn = document.getElementById('reset-filters');
    if (resetFiltersBtn) {
        resetFiltersBtn.addEventListener('click', resetFilters);
    }
    
    // Поиск
    const searchInput = document.getElementById('search-input');
    const searchButton = document.getElementById('search-button');
    
    if (searchInput) {
        searchInput.addEventListener('input', handleSearch);
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                handleSearch();
            }
        });
    }
    
    if (searchButton) {
        searchButton.addEventListener('click', handleSearch);
    }
    
    // Кнопка поиска в хедере
    const headerSearchBtn = document.getElementById('header-search-btn');
    if (headerSearchBtn) {
        // Устанавливаем флаг на capture фазе ПЕРЕД обработчиком закрытия
        headerSearchBtn.addEventListener('click', function(e) {
            isSearchButtonClicked = true;
            console.log('Флаг isSearchButtonClicked установлен в true (capture фаза)');
            setTimeout(() => {
                isSearchButtonClicked = false;
                console.log('Флаг isSearchButtonClicked сброшен в false');
            }, 500);
        }, true); // capture фаза
        
        // Основной обработчик - открываем/закрываем меню
        headerSearchBtn.onclick = function(e) {
            e.preventDefault();
            e.stopPropagation();
            e.stopImmediatePropagation();
            
            console.log('Клик по кнопке поиска в хедере');
            
            // Вызываем обработчик открытия/закрытия
            handleHeaderSearchClick();
            
            return false;
        };
    }
    
    // Обработчики для выпадающего поиска
    setupDropdownSearchHandlers();
}

// Обработка изменения фильтров
function handleFilterChange(event) {
    let filterType = event.target.id.replace('-filter', '');
    // Преобразуем 'author' в 'artist' для совместимости
    if (filterType === 'author') {
        filterType = 'artist';
    }
    currentFilters[filterType] = event.target.value;
    // Также обновляем author для обратной совместимости
    if (filterType === 'artist') {
        currentFilters.author = event.target.value;
    }
    currentPage = 1; // Сброс на первую страницу
    renderCatalog();
    renderPagination();
}

// Обработка поиска
function handleSearch(event) {
    const searchInput = document.getElementById('search-input');
    const searchTerm = searchInput.value.trim().toLowerCase();
    
    currentFilters.search = searchTerm;
    currentPage = 1; // Сброс на первую страницу
    
    // Показываем результаты поиска
    renderCatalog();
    renderPagination();
    
    // Убираем показ информации о поиске (не нужно)
}

// Обработка клика по кнопке поиска в хедере
function handleHeaderSearchClick() {
    console.log('handleHeaderSearchClick вызвана');
    const dropdown = document.getElementById('search-dropdown-content');
    const searchInput = document.getElementById('search-input');
    console.log('Найденные элементы:', { dropdown: !!dropdown, searchInput: !!searchInput });
    
    if (dropdown) {
        // Всегда открываем меню при клике на кнопку поиска
        console.log('Открываем меню поиска');
        showSearchDropdown();
    } else if (searchInput) {
        // Fallback для страниц без выпадающего поиска
        console.log('Используем fallback для search-input');
        searchInput.focus();
        
        if (!searchInput.value.trim()) {
            searchInput.placeholder = 'Введите название пластинки, исполнителя или описание...';
            searchInput.style.borderColor = '#FF9900';
            
            setTimeout(() => {
                searchInput.placeholder = 'Введите название или исполнителя...';
                searchInput.style.borderColor = '';
            }, 3000);
        } else {
            handleSearch();
        }
    } else {
        console.error('Не найдены ни dropdown, ни search-input!');
    }
}

// Показать выпадающий поиск
function showSearchDropdown() {
    const dropdown = document.getElementById('search-dropdown-content');
    console.log('showSearchDropdown вызвана, dropdown:', dropdown);
    if (dropdown) {
        // Всегда открываем меню при клике на кнопку
        dropdown.classList.add('show');
        
        const computedStyle = window.getComputedStyle(dropdown);
        const isActuallyVisible = computedStyle.display !== 'none';
        
        console.log('Состояние меню после открытия:', { 
            hasShowClass: dropdown.classList.contains('show'), 
            actuallyVisible: isActuallyVisible,
            display: computedStyle.display 
        });
        
        if (isActuallyVisible) {
            // Фокусируемся на поле поиска при открытии
            const dropdownInput = document.getElementById('dropdown-search-input');
            if (dropdownInput) {
                setTimeout(() => {
                    dropdownInput.focus();
                    console.log('Фокус установлен на поле поиска');
                }, 100);
            }
            
            // Заполняем фильтры данными
            populateDropdownFilters();
        } else {
            console.warn('Меню не видно после открытия!');
        }
    } else {
        console.error('Элемент search-dropdown-content не найден!');
    }
}

// Скрыть выпадающий поиск
function hideSearchDropdown() {
    const dropdown = document.getElementById('search-dropdown-content');
    if (dropdown) {
        dropdown.classList.remove('show');
        console.log('Меню поиска закрыто');
    }
}

// Показать/скрыть выпадающий поиск (для обратной совместимости)
function toggleSearchDropdown() {
    const dropdown = document.getElementById('search-dropdown-content');
    if (dropdown) {
        const isVisible = dropdown.classList.contains('show');
        if (isVisible) {
            hideSearchDropdown();
        } else {
            showSearchDropdown();
        }
    }
}

// Заполнение фильтров в выпадающем поиске
function populateDropdownFilters() {
    const genreFilter = document.getElementById('dropdown-genre-filter');
    const artistFilter = document.getElementById('dropdown-author-filter') || document.getElementById('dropdown-artist-filter');
    
    if (genreFilter && vinylRecords.length > 0) {
        const genres = [...new Set(vinylRecords.map(record => record.genre))];
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
    
    if (artistFilter && vinylRecords.length > 0) {
        const artists = [...new Set(vinylRecords.map(record => record.artist || record.author))];
        const currentArtistValue = artistFilter.value;
        artistFilter.innerHTML = '<option value="">Все исполнители</option>';
        
        artists.forEach(artist => {
            const option = document.createElement('option');
            option.value = artist;
            option.textContent = artist;
            artistFilter.appendChild(option);
        });
        
        if (currentArtistValue) {
            artistFilter.value = currentArtistValue;
        }
    }
}

// Сброс всех фильтров
function resetFilters() {
    currentFilters = {
        genre: '',
        artist: '',
        author: '', // Для обратной совместимости
        sort: 'popular',
        search: ''
    };
    
    // Сброс значений в форме
    const genreFilter = document.getElementById('genre-filter');
    const artistFilter = document.getElementById('author-filter') || document.getElementById('artist-filter');
    const sortFilter = document.getElementById('sort-filter');
    
    if (genreFilter) genreFilter.value = '';
    if (artistFilter) artistFilter.value = '';
    if (sortFilter) sortFilter.value = 'popular';
    
    // Очищаем поле поиска
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.value = '';
    }
    
    currentPage = 1;
    renderCatalog();
    renderPagination();
    
    // Скрываем информацию о поиске
    hideSearchInfo();
}

// Получение отфильтрованных виниловых пластинок
function getFilteredBooks() {
    let filteredRecords = [...vinylRecords];
    
    // Поиск по названию и исполнителю
    if (currentFilters.search) {
        filteredRecords = filteredRecords.filter(record => 
            record.title.toLowerCase().includes(currentFilters.search) ||
            (record.artist || record.author || '').toLowerCase().includes(currentFilters.search) ||
            (record.description || '').toLowerCase().includes(currentFilters.search)
        );
    }
    
    // Фильтр по жанру
    if (currentFilters.genre) {
        filteredRecords = filteredRecords.filter(record => record.genre === currentFilters.genre);
    }
    
    // Фильтр по исполнителю
    const artistFilter = currentFilters.artist || currentFilters.author;
    if (artistFilter) {
        filteredRecords = filteredRecords.filter(record => 
            (record.artist || record.author || '').toLowerCase().includes(artistFilter.toLowerCase())
        );
    }
    
    // Сортировка
    switch (currentFilters.sort) {
        case 'newest':
            filteredRecords.sort((a, b) => b.id - a.id);
            break;
        case 'price-low':
            filteredRecords.sort((a, b) => a.price - b.price);
            break;
        case 'price-high':
            filteredRecords.sort((a, b) => b.price - a.price);
            break;
        case 'rating':
            filteredRecords.sort((a, b) => b.rating - a.rating);
            break;
        case 'popular':
        default:
            filteredRecords.sort((a, b) => b.rating - a.rating);
            break;
    }
    
    return filteredRecords;
}

// Получение пластинок для текущей страницы
function getBooksForCurrentPage() {
    const filteredRecords = getFilteredBooks();
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    return filteredRecords.slice(startIndex, endIndex);
}

// Псевдоним для обратной совместимости
function getFilteredRecords() {
    return getFilteredBooks();
}

// Отрисовка каталога
function renderCatalog() {
    const catalogGrid = document.getElementById('catalog-grid');
    const records = getBooksForCurrentPage();
    
    if (records.length === 0) {
        let message = 'Виниловые пластинки не найдены. Попробуйте изменить фильтры.';
        
        // Специальное сообщение для поиска
        if (currentFilters.search) {
            message = `По запросу "<strong>${currentFilters.search}</strong>" ничего не найдено. Попробуйте изменить поисковый запрос или фильтры.`;
        }
        
        catalogGrid.innerHTML = `<div class="no-results">${message}</div>`;
        return;
    }
    
    catalogGrid.innerHTML = records.map(record => createBookCard(record)).join('');
    
    // Добавляем обработчики для кнопок "В корзину"
    catalogGrid.querySelectorAll('.buy-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            e.stopImmediatePropagation();
            const recordId = this.getAttribute('data-record-id');
            console.log('Клик по кнопке "В корзину", ID:', recordId);
            if (recordId) {
                addToCart(recordId);
            }
            return false;
        });
    });
    
    // Предотвращаем переход по ссылке при клике на кнопку внутри карточки
    catalogGrid.querySelectorAll('.record-card-link').forEach(link => {
        link.addEventListener('click', function(e) {
            // Если клик был по кнопке или её дочерним элементам, не переходим по ссылке
            if (e.target.closest('.buy-btn') || e.target.closest('.expand-description-btn')) {
                e.preventDefault();
            }
        });
    });
}

// Функция для получения безопасного URL изображения
function getSafeImageUrl(imageUrl, title) {
    if (!imageUrl || imageUrl === 'null' || imageUrl === 'undefined') {
        return VINYL_PLACEHOLDER_SVG;
    }
    return imageUrl;
}

// Создание карточки виниловой пластинки
function createBookCard(record) {
    const safeImageUrl = getSafeImageUrl(record.image, record.title);
    const artist = record.artist || record.author || 'Неизвестный исполнитель';
    
    // Обработка описания с возможностью разворачивания
    const maxLength = 120; // Максимальная длина свернутого описания
    const description = record.description || 'Описание отсутствует';
    const isLongDescription = description.length > maxLength;
    const shortDescription = isLongDescription ? description.substring(0, maxLength) + '...' : description;
    
    let descriptionHtml = '';
    if (isLongDescription) {
        // Создаем описание с кнопкой разворачивания
        const descriptionId = `desc-${record.id}`;
        // Используем JSON.stringify для безопасного экранирования в data-атрибутах
        const fullDescEscaped = JSON.stringify(description);
        const shortDescEscaped = JSON.stringify(shortDescription);
        descriptionHtml = `
            <div class="record-description-container">
                <p class="record-description" id="${descriptionId}" data-full=${fullDescEscaped} data-short=${shortDescEscaped} data-expanded="false">
                    ${escapeHtml(shortDescription)}
                </p>
                <button class="expand-description-btn" onclick="toggleDescription('${descriptionId}'); event.stopPropagation(); event.preventDefault(); return false;">
                    Развернуть ▾
                </button>
            </div>
        `;
    } else {
        descriptionHtml = `<p class="record-description">${escapeHtml(description)}</p>`;
    }
    
    return `
        <a href="book-detail.html?id=${record.id}" class="record-card-link">
            <div class="record-card" data-record-id="${record.id}">
                <div class="record-image">
                    <img src="${safeImageUrl}" 
                         alt="${record.title}" 
                         loading="lazy"
                         onerror="this.onerror=null; this.src='${VINYL_PLACEHOLDER_SVG}';">
                </div>
                <div class="record-info">
                    <h3 class="record-title">${escapeHtml(record.title)}</h3>
                    <p class="record-author">${escapeHtml(artist)}</p>
                    <div class="record-rating">
                        <span class="rating-stars">★</span>
                        <span class="rating-value">${record.rating.toFixed(1)}</span>
                    </div>
                    ${descriptionHtml}
                    <div class="record-price">${record.price} руб.</div>
                    <button class="buy-btn" data-record-id="${record.id}">В корзину</button>
                </div>
            </div>
        </a>
    `;
}

// Функция для экранирования HTML (защита от XSS)
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Функция для разворачивания/сворачивания описания
function toggleDescription(descriptionId) {
    const descElement = document.getElementById(descriptionId);
    if (!descElement) return;
    
    const isExpanded = descElement.getAttribute('data-expanded') === 'true';
    // Получаем данные из data-атрибутов (JSON.stringify автоматически парсится)
    let fullDesc = descElement.getAttribute('data-full');
    let shortDesc = descElement.getAttribute('data-short');
    
    // Если данные были закодированы через JSON.stringify, парсим их
    try {
        fullDesc = JSON.parse(fullDesc);
    } catch (e) {
        // Если не JSON, используем как есть
    }
    try {
        shortDesc = JSON.parse(shortDesc);
    } catch (e) {
        // Если не JSON, используем как есть
    }
    
    const btn = descElement.nextElementSibling;
    
    if (isExpanded) {
        // Сворачиваем
        descElement.textContent = shortDesc;
        descElement.setAttribute('data-expanded', 'false');
        if (btn && btn.classList.contains('expand-description-btn')) {
            btn.textContent = 'Развернуть ▾';
        }
    } else {
        // Разворачиваем
        descElement.textContent = fullDesc;
        descElement.setAttribute('data-expanded', 'true');
        if (btn && btn.classList.contains('expand-description-btn')) {
            btn.textContent = 'Свернуть ▲';
        }
    }
}

// Экспортируем функцию в глобальную область видимости
window.toggleDescription = toggleDescription;

// Получение звездочек рейтинга
function getRatingStars(rating) {
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    let stars = '★'.repeat(fullStars);
    if (hasHalfStar) stars += '☆';
    return stars;
}

// Отрисовка пагинации
function renderPagination() {
    const pagination = document.getElementById('pagination');
    const filteredRecords = getFilteredBooks();
    const totalPages = Math.ceil(filteredRecords.length / itemsPerPage);
    
    if (totalPages <= 1) {
        pagination.innerHTML = '';
        return;
    }
    
    let paginationHTML = '<div class="pagination-container">';
    
    // Предыдущая страница
    if (currentPage > 1) {
        paginationHTML += `<button class="page-btn" onclick="goToPage(${currentPage - 1})">‹ Предыдущая</button>`;
    }
    
    // Номера страниц
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, currentPage + 2);
    
    if (startPage > 1) {
        paginationHTML += `<button class="page-btn" onclick="goToPage(1)">1</button>`;
        if (startPage > 2) {
            paginationHTML += `<span class="page-dots">...</span>`;
        }
    }
    
    for (let i = startPage; i <= endPage; i++) {
        const isActive = i === currentPage ? 'active' : '';
        paginationHTML += `<button class="page-btn ${isActive}" onclick="goToPage(${i})">${i}</button>`;
    }
    
    if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
            paginationHTML += `<span class="page-dots">...</span>`;
        }
        paginationHTML += `<button class="page-btn" onclick="goToPage(${totalPages})">${totalPages}</button>`;
    }
    
    // Следующая страница
    if (currentPage < totalPages) {
        paginationHTML += `<button class="page-btn" onclick="goToPage(${currentPage + 1})">Следующая ›</button>`;
    }
    
    paginationHTML += '</div>';
    pagination.innerHTML = paginationHTML;
}

// Переход на страницу
function goToPage(page) {
    const filteredRecords = getFilteredBooks();
    const totalPages = Math.ceil(filteredRecords.length / itemsPerPage);
    
    if (page >= 1 && page <= totalPages) {
        currentPage = page;
        renderCatalog();
        renderPagination();
        
        // Прокрутка к началу каталога
        document.getElementById('catalog-grid').scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
        });
    }
}

// Добавление в корзину
function addToCart(recordId) {
    // Убеждаемся, что recordId является строкой или числом
    const normalizedId = String(recordId);
    console.log('addToCart вызвана с ID:', recordId, 'нормализованный ID:', normalizedId);
    
    // Используем window.vinylRecords если доступен (для тестирования), иначе локальный
    const recordsToSearch = window.vinylRecords || vinylRecords;
    
    // Проверяем, что recordsToSearch - массив
    if (!Array.isArray(recordsToSearch)) {
        console.error('vinylRecords не является массивом:', typeof recordsToSearch, recordsToSearch);
        return;
    }
    
    const record = recordsToSearch.find(b => String(b.id) === normalizedId);
    if (!record) {
        console.error('Пластинка не найдена для ID:', normalizedId, 'Доступные ID:', recordsToSearch.map(b => b.id));
        return;
    }
    
    console.log('Пластинка найдена:', record.title || record.name);
    
    // Сохраняем информацию о товаре в localStorage для использования в корзине
    const productInfo = {
        id: record.id,
        title: record.title || record.name,
        price: record.price,
        image_url: record.image || record.cover_url || record.cover_image_url || '',
        artist: record.artist || record.author || 'Неизвестный исполнитель',
        description: record.description || ''
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
                id: record.id,
                title: record.title,
                price: record.price,
                image: record.image,
                quantity: 1
            });
        }
        
        localStorage.setItem('cart', JSON.stringify(cart));
    }
    
    // Обновляем счетчик корзины
    loadCartCount();
    // Также вызываем updateCartCount если доступна (для страниц с cart.js)
    if (typeof window.updateCartCount === 'function') {
        window.updateCartCount();
    }
    
    // Показываем уведомление
    showNotification(`"${record.title}" добавлена в корзину!`);
}

// Загрузка счетчика корзины
function loadCartCount() {
    // Используем новую систему корзины с количеством
    if (typeof window.getCartWithQuantity === 'function') {
        const cartWithQuantity = window.getCartWithQuantity();
        const totalItems = Object.values(cartWithQuantity).reduce((sum, quantity) => sum + quantity, 0);
        const cartCountElement = document.getElementById('cart-count');
        if (cartCountElement) {
            cartCountElement.textContent = totalItems;
        }
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
    // Создаем элемент уведомления
    const notification = document.createElement('div');
    notification.className = 'notification';
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
        z-index: 1000;
        animation: slideIn 0.3s ease-out;
    `;
    
    // Добавляем анимацию
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes slideOut {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }
    `;
    document.head.appendChild(style);
    
    // Добавляем на страницу
    document.body.appendChild(notification);
    
    // Удаляем через 3 секунды
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Показ информации о поиске
function showSearchInfo(searchTerm) {
    if (!searchTerm) return;
    
    const catalogGrid = document.getElementById('catalog-grid');
    if (!catalogGrid) return; // Если нет каталога, не показываем информацию о поиске
    
    // Удаляем предыдущую информацию о поиске, если она есть
    const existingSearchInfo = document.getElementById('search-info');
    if (existingSearchInfo) {
        existingSearchInfo.remove();
    }
    
    const searchInfo = document.createElement('div');
    searchInfo.id = 'search-info';
    searchInfo.className = 'search-info';
    searchInfo.innerHTML = `
        <div class="search-info-content">
            <span class="search-icon">🔍</span>
            <span class="search-text">Результаты поиска по запросу: "<strong>${escapeHtml(searchTerm)}</strong>"</span>
            <button class="clear-search-btn" onclick="clearSearch()">✕</button>
        </div>
    `;
    
    // Вставляем перед каталогом
    catalogGrid.parentNode.insertBefore(searchInfo, catalogGrid);
}

// Скрытие информации о поиске
function hideSearchInfo() {
    const searchInfo = document.getElementById('search-info');
    if (searchInfo) {
        searchInfo.remove();
    }
}

// Очистка поиска
function clearSearch() {
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.value = '';
    }
    
    currentFilters.search = '';
    currentPage = 1;
    
    renderCatalog();
    renderPagination();
    hideSearchInfo();
}

// Проверка авторизации пользователя
function checkAuth() {
    const token = localStorage.getItem('accessToken');
    const loginLink = document.getElementById('login-link');
    const userProfileBlock = document.getElementById('user-profile-block');
    
    if (token) {
        // Пользователь авторизован
        if (loginLink) loginLink.style.display = 'none';
        if (userProfileBlock) userProfileBlock.style.display = 'flex';
        
        // Добавляем обработчик выхода
        const logoutBtn = document.getElementById('logout-btn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', function() {
                localStorage.removeItem('accessToken');
                localStorage.removeItem('userData');
                alert('Вы вышли из системы.');
                location.reload();
            });
        }
    } else {
        // Пользователь не авторизован
        if (loginLink) loginLink.style.display = 'block';
        if (userProfileBlock) userProfileBlock.style.display = 'none';
    }
}

// Инициализация проверки авторизации
document.addEventListener('DOMContentLoaded', checkAuth);

// ===== РЕКОМЕНДАЦИОННАЯ СИСТЕМА =====

// API для рекомендаций
const RECOMMENDATIONS_API_URL = 'http://localhost:8004/api/v1/recommendations/generate';

// Функция для открытия модального окна рекомендаций
function getRecommendations() {
    const modal = document.getElementById('recommendations-modal');
    if (modal) {
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
    }
}

// Функция для отображения рекомендаций
function displayRecommendations(data) {
    const recommendationsSection = document.getElementById('recommendations-section');
    const recommendationsGrid = document.getElementById('recommendations-grid');
    const aiConfidence = document.getElementById('ai-confidence');
    const recommendationReasoning = document.getElementById('recommendation-reasoning');
    const reasoningText = document.getElementById('reasoning-text');
    
    // Обновляем уверенность AI
    const confidence = Math.round(data.confidence_score * 100);
    aiConfidence.textContent = `Уверенность AI: ${confidence}%`;
    
    // Очищаем предыдущие рекомендации
    recommendationsGrid.innerHTML = '';
    
    // Добавляем карточки рекомендаций
    data.recommendations.forEach(record => {
        const recordCard = createRecommendationCard(record);
        recommendationsGrid.appendChild(recordCard);
    });
    
    // Показываем обоснование
    if (data.reasoning) {
        reasoningText.textContent = data.reasoning;
        recommendationReasoning.style.display = 'block';
    }
    
    // Показываем секцию рекомендаций
    recommendationsSection.style.display = 'block';
    
    // Плавно прокручиваем к рекомендациям
    recommendationsSection.scrollIntoView({ behavior: 'smooth' });
}

// Функция для создания карточки рекомендации
function createRecommendationCard(record) {
    const card = document.createElement('div');
    card.className = 'recommendation-card';
    card.onclick = () => addToCart(String(record.id));
    
    const imageUrl = record.image || record.cover_url || VINYL_PLACEHOLDER_SVG;
    const safeImageUrl = imageUrl && imageUrl !== 'null' && imageUrl !== 'undefined' ? imageUrl : VINYL_PLACEHOLDER_SVG;
    const artist = record.artist || record.author || 'Неизвестный исполнитель';
    
    card.innerHTML = `
        <div class="recommendation-image">
            <img src="${safeImageUrl}" 
                 alt="${record.title || record.name}" 
                 loading="lazy"
                 onerror="this.onerror=null; this.src='${VINYL_PLACEHOLDER_SVG}';"
                 style="width: 100%; height: 100%; object-fit: cover;">
        </div>
        <div class="recommendation-title">${record.title || record.name}</div>
        <div class="recommendation-author">${artist}</div>
        <div class="recommendation-price">${record.price}₽</div>
    `;
    
    return card;
}

// Добавляем обработчик события для кнопки рекомендаций (только если модальное окно не обрабатывается)
document.addEventListener('DOMContentLoaded', function() {
    const recommendationsButton = document.getElementById('get-recommendations');
    if (recommendationsButton && !document.getElementById('recommendations-modal')) {
        recommendationsButton.addEventListener('click', getRecommendations);
    }
});

// Функция для перехода на страницу поиска
function goToSearch() {
    window.location.href = 'search.html';
}

// Настройка обработчиков для выпадающего поиска
function setupDropdownSearchHandlers() {
    // Кнопка закрытия выпадающего поиска
    const closeBtn = document.getElementById('search-dropdown-close');
    if (closeBtn) {
        closeBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            hideSearchDropdown();
        });
    }
    
    // Кнопка поиска в выпадающем меню
    const searchBtn = document.getElementById('dropdown-search-btn');
    if (searchBtn) {
        searchBtn.addEventListener('click', handleDropdownSearch);
    }
    
    // Кнопка очистки в выпадающем меню
    const clearBtn = document.getElementById('dropdown-clear-btn');
    if (clearBtn) {
        clearBtn.addEventListener('click', handleDropdownClear);
    }
    
    // Обработчик Enter в поле поиска выпадающего меню
    const dropdownInput = document.getElementById('dropdown-search-input');
    if (dropdownInput) {
        dropdownInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                handleDropdownSearch();
            }
        });
    }
    
    // Обработчики изменения фильтров в выпадающем меню
    const genreFilter = document.getElementById('dropdown-genre-filter');
    const artistFilter = document.getElementById('dropdown-author-filter') || document.getElementById('dropdown-artist-filter');
    
    if (genreFilter) {
        genreFilter.addEventListener('change', handleDropdownFilterChange);
    }
    
    if (artistFilter) {
        artistFilter.addEventListener('change', handleDropdownFilterChange);
    }
    
    // Закрытие выпадающего поиска при клике вне его
    // Используем capture фазу, чтобы проверить флаг до других обработчиков
    document.addEventListener('click', function(event) {
        // Если флаг установлен, не закрываем меню
        if (isSearchButtonClicked) {
            console.log('Флаг isSearchButtonClicked установлен, не закрываем меню');
            return;
        }
        
        const dropdown = document.getElementById('search-dropdown-content');
        const searchBtn = document.getElementById('header-search-btn');
        
        // Не закрываем меню, если клик был по кнопке поиска или внутри меню
        if (searchBtn && (searchBtn.contains(event.target) || event.target === searchBtn)) {
            console.log('Клик по кнопке поиска, не закрываем меню');
            return;
        }
        
        if (dropdown && dropdown.contains(event.target)) {
            console.log('Клик внутри меню, не закрываем');
            return;
        }
        
        // Закрываем меню только если клик был вне его
        if (dropdown && dropdown.classList.contains('show')) {
            console.log('Закрываем меню поиска (клик вне меню)');
            hideSearchDropdown();
        }
    }, true); // Используем capture фазу
}

// Обработка поиска в выпадающем меню
function handleDropdownSearch() {
    const dropdownInput = document.getElementById('dropdown-search-input');
    const genreFilter = document.getElementById('dropdown-genre-filter');
    const artistFilter = document.getElementById('dropdown-author-filter') || document.getElementById('dropdown-artist-filter');
    
    if (dropdownInput) {
        const searchTerm = dropdownInput.value.trim().toLowerCase();
        const genre = genreFilter ? genreFilter.value : '';
        const artist = artistFilter ? artistFilter.value : '';
        
        // Обновляем основные фильтры
        currentFilters.search = searchTerm;
        currentFilters.genre = genre;
        currentFilters.artist = artist;
        currentFilters.author = artist; // Для обратной совместимости
        currentPage = 1;
        
        // Обновляем основное поле поиска на странице поиска
        const mainSearchInput = document.getElementById('search-input');
        if (mainSearchInput) {
            mainSearchInput.value = searchTerm;
        }
        
        // Обновляем основные фильтры на странице поиска
        const mainGenreFilter = document.getElementById('genre-filter');
        const mainArtistFilter = document.getElementById('author-filter') || document.getElementById('artist-filter');
        
        if (mainGenreFilter) mainGenreFilter.value = genre;
        if (mainArtistFilter) mainArtistFilter.value = artist;
        
        // Выполняем поиск
        renderCatalog();
        renderPagination();
        showSearchInfo(searchTerm);
        
        // Закрываем выпадающий поиск
        const dropdown = document.getElementById('search-dropdown-content');
        if (dropdown) {
            dropdown.classList.remove('show');
        }
        
        // Если мы не на странице с каталогом (index.html или search.html), переходим на search.html
        const catalogGrid = document.getElementById('catalog-grid');
        if (!catalogGrid && !mainSearchInput) {
            // Сохраняем параметры поиска перед переходом
            const searchParams = new URLSearchParams();
            if (searchTerm) searchParams.set('q', searchTerm);
            if (genre) searchParams.set('genre', genre);
            if (artist) searchParams.set('artist', artist);
            const queryString = searchParams.toString();
            window.location.href = 'search.html' + (queryString ? '?' + queryString : '');
        }
    }
}

// Обработка очистки в выпадающем меню
function handleDropdownClear() {
    const dropdownInput = document.getElementById('dropdown-search-input');
    const genreFilter = document.getElementById('dropdown-genre-filter');
    const artistFilter = document.getElementById('dropdown-author-filter') || document.getElementById('dropdown-artist-filter');
    
    if (dropdownInput) dropdownInput.value = '';
    if (genreFilter) genreFilter.value = '';
    if (artistFilter) artistFilter.value = '';
    
    // Очищаем основные фильтры
    currentFilters.search = '';
    currentFilters.genre = '';
    currentFilters.artist = '';
    currentFilters.author = ''; // Для обратной совместимости
    currentPage = 1;
    
    // Обновляем основное поле поиска на странице поиска
    const mainSearchInput = document.getElementById('search-input');
    if (mainSearchInput) {
        mainSearchInput.value = '';
    }
    
    // Обновляем основные фильтры на странице поиска
    const mainGenreFilter = document.getElementById('genre-filter');
    const mainArtistFilter = document.getElementById('author-filter') || document.getElementById('artist-filter');
    
    if (mainGenreFilter) mainGenreFilter.value = '';
    if (mainArtistFilter) mainArtistFilter.value = '';
    
    // Обновляем отображение
    renderCatalog();
    renderPagination();
    hideSearchInfo();
}

// Обработка изменения фильтров в выпадающем меню
function handleDropdownFilterChange(event) {
    let filterType = event.target.id.replace('dropdown-', '').replace('-filter', '');
    // Преобразуем 'author' в 'artist' для совместимости
    if (filterType === 'author') {
        filterType = 'artist';
    }
    currentFilters[filterType] = event.target.value;
    // Также обновляем author для обратной совместимости
    if (filterType === 'artist') {
        currentFilters.author = event.target.value;
    }
}

// Экспортируем функцию в глобальную область видимости
window.goToSearch = goToSearch;