// Функция проверки токена администратора
function checkAdminToken() {
    const token = localStorage.getItem('admin_token');
    if (!token) {
        return false;
    }
    
    // Простая проверка формата токена
    return token.startsWith('admin_token_') && token.length > 20;
}

// Проверка авторизации при загрузке страницы
if (!checkAdminToken()) {
    window.location.href = 'login.html';
}

// Функция выхода из системы
function logoutAdmin() {
    localStorage.removeItem('admin_token');
    window.location.href = 'login.html';
}

// Локальное хранилище товаров
let products = [];

// Элементы DOM
const productForm = document.getElementById('product-form');
const productsTable = document.getElementById('products-table');
const loadingDiv = document.getElementById('loading');
const errorDiv = document.getElementById('error-message');
const successDiv = document.getElementById('success-message');

// Функция для отображения сообщений
function showMessage(message, type = 'error') {
    // Скрываем все сообщения
    errorDiv.style.display = 'none';
    successDiv.style.display = 'none';
    
    if (type === 'error') {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
    } else if (type === 'success') {
        successDiv.textContent = message;
        successDiv.style.display = 'block';
    }
    
    // Автоматически скрываем сообщение через 5 секунд
    setTimeout(() => {
        errorDiv.style.display = 'none';
        successDiv.style.display = 'none';
    }, 5000);
}

// Функция для показа/скрытия загрузки
function toggleLoading(show) {
    loadingDiv.style.display = show ? 'block' : 'none';
}

// Функция для очистки формы
function clearForm() {
    productForm.reset();
    productForm.removeAttribute('data-editing-id');
}

// Функция для заполнения формы данными товара
function fillFormWithProduct(product) {
    document.getElementById('title').value = product.title || '';
    document.getElementById('author_id').value = product.author_id || '';
    document.getElementById('description').value = product.description || '';
    document.getElementById('price').value = product.price || '';
    
    // Устанавливаем атрибут для редактирования
    productForm.setAttribute('data-editing-id', product.id);
}

// Функция для загрузки товаров из API каталога
async function loadProducts() {
    toggleLoading(true);
    try {
            // Пытаемся загрузить пластинки из API каталога
        const catalogUrl = window.API_CONFIG?.catalog || 'http://localhost:8000';
        const response = await fetch(`${catalogUrl}/api/v1/admin/products`);
        if (response.ok) {
            const data = await response.json();
            // Преобразуем формат данных API (name -> title) для совместимости с админ-панелью
            products = data.products.map(product => ({
                id: product.id,
                title: product.name || product.title || '',
                author_id: product.author_id || null,
                description: product.description || '',
                price: product.price || 0,
                author: product.author || null,
                cover_url: product.cover_url || null
            }));
            // Сохраняем в localStorage для офлайн режима
            saveProducts();
            showMessage(`Загружено ${products.length} товаров из каталога`, 'success');
        } else {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
    } catch (error) {
        console.warn('Ошибка при загрузке товаров из API, используем localStorage:', error.message);
        // Fallback на localStorage
        const savedProducts = localStorage.getItem('admin_products');
        if (savedProducts) {
            products = JSON.parse(savedProducts);
            showMessage('Загружено из локального хранилища (API недоступен)', 'error');
        } else {
            // Если нет данных в localStorage, показываем пустой список
            products = [];
            showMessage('Товары не найдены. API недоступен и localStorage пуст.', 'error');
        }
    } finally {
        toggleLoading(false);
        renderProducts();
    }
}

// Функция для сохранения товаров в localStorage
function saveProducts() {
    localStorage.setItem('admin_products', JSON.stringify(products));
}

// Функция для отрисовки товаров
function renderProducts() {
    const tbody = productsTable.querySelector('tbody');
    tbody.innerHTML = '';
    
    if (products.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: #666;">Товары не найдены</td></tr>';
        return;
    }
    
    // Добавляем строки для каждого товара
    products.forEach(product => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td data-label="ID">${product.id}</td>
            <td data-label="Название">${product.title}</td>
            <td data-label="Автор ID">${product.author_id}</td>
            <td class="description-cell" data-label="Описание">${product.description ? product.description.substring(0, 50) + (product.description.length > 50 ? '...' : '') : ''}</td>
            <td data-label="Цена">${product.price ? product.price.toFixed(2) : '0.00'}</td>
            <td data-label="Действия">
                <div class="actions">
                    <button class="generate-description-btn" data-product-id="${product.id}" title="Сгенерировать описание через AI">AI-описание</button>
                    <button class="btn-warning edit-btn" data-id="${product.id}">Редактировать</button>
                    <button class="btn-danger delete-btn" data-id="${product.id}">Удалить</button>
                </div>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Обработчик отправки формы
productForm.addEventListener('submit', (event) => {
    event.preventDefault();
    
    try {
        const formData = new FormData(productForm);
        const productData = {
            title: formData.get('title'),
            author_id: parseInt(formData.get('author_id')),
            description: formData.get('description'),
            price: parseFloat(formData.get('price'))
        };
        
        // Проверяем, редактируется ли товар
        const editingId = productForm.getAttribute('data-editing-id');
        
        if (editingId) {
            // Обновляем существующий товар
            const index = products.findIndex(p => p.id == editingId);
            if (index !== -1) {
                products[index] = { ...products[index], ...productData };
            }
            showMessage('Товар успешно обновлен!', 'success');
        } else {
            // Создаем новый товар
            const newProduct = {
                id: Math.max(...products.map(p => p.id)) + 1,
                ...productData
            };
            products.push(newProduct);
            showMessage('Товар успешно создан!', 'success');
        }
        
        // Сохраняем в localStorage
        saveProducts();
        
        // Очищаем форму
        clearForm();
        
        // Обновляем список товаров
        renderProducts();
        
    } catch (error) {
        console.error('Ошибка при сохранении товара:', error);
        showMessage('Ошибка при сохранении товара: ' + error.message);
    }
});

// Делегирование событий для таблицы товаров
productsTable.addEventListener('click', (event) => {
    const target = event.target;
    
    // Обработка кнопки "AI-описание"
    if (target.classList.contains('generate-description-btn')) {
        const productId = target.getAttribute('data-product-id');
        
        // Отключаем кнопку на время запроса
        target.disabled = true;
        target.textContent = 'Генерация...';
        
        // Делаем POST запрос к оркестратору
        const recommenderUrl = window.API_CONFIG?.recommender || 'http://localhost:8004';
        fetch(`${recommenderUrl}/api/v1/recommendations/generate-description/${productId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(async response => {
            if (!response.ok) {
                // Пытаемся получить детали ошибки из ответа
                let errorDetail = '';
                try {
                    const errorData = await response.json();
                    errorDetail = errorData.detail || errorData.message || '';
                } catch (e) {
                    errorDetail = response.statusText || '';
                }
                
                const errorMessage = errorDetail 
                    ? `HTTP error! status: ${response.status} - ${errorDetail}`
                    : `HTTP error! status: ${response.status}`;
                throw new Error(errorMessage);
            }
            return response.json();
        })
        .then(data => {
            // Находим соответствующую ячейку с описанием в таблице
            const row = target.closest('tr');
            const descriptionCell = row.querySelector('.description-cell');
            
            if (descriptionCell && data.generated_description) {
                // Динамически обновляем содержимое ячейки новым описанием
                const fullDescription = data.generated_description;
                const shortDescription = fullDescription.length > 50 
                    ? fullDescription.substring(0, 50) + '...' 
                    : fullDescription;
                descriptionCell.textContent = shortDescription;
                descriptionCell.title = fullDescription; // Полное описание в tooltip
                
                // Обновляем описание в локальном массиве
                const product = products.find(p => p.id == productId);
                if (product) {
                    product.description = fullDescription;
                    saveProducts();
                }
                
                showMessage('Описание успешно обновлено!', 'success');
            }
        })
        .catch(error => {
            console.error('Ошибка при генерации описания:', error);
            let errorMessage = 'Ошибка при генерации описания: ';
            
            // Извлекаем детали ошибки из сообщения, если они есть
            const errorMsg = error.message || 'Неизвестная ошибка';
            
            if (errorMsg.includes('Failed to fetch') || errorMsg.includes('ERR_CONNECTION_REFUSED') || errorMsg.includes('NetworkError')) {
                errorMessage += 'Не удалось подключиться к сервису. Убедитесь, что сервис рекомендаций запущен на порту 8004.';
            } else if (errorMsg.includes('Ошибка при обращении к внешнему AI сервису') || errorMsg.includes('502')) {
                // Ошибка 502 от сервиса рекомендаций
                errorMessage = errorMsg; // Используем сообщение напрямую, так как оно уже содержит детали
            } else if (errorMsg.includes('Не удалось обработать ответ от AI')) {
                // Ошибка парсинга JSON или обработки ответа от AI
                errorMessage = errorMsg; // Используем сообщение напрямую
            } else if (errorMsg.includes('status: 500') || errorMsg.includes('Внутренняя ошибка')) {
                // Для ошибок 500 показываем детали из сообщения
                if (errorMsg.includes('404') || errorMsg.includes('not found') || errorMsg.includes('No endpoints')) {
                    errorMessage += 'Модель AI недоступна. Сервер автоматически попробует другую модель. Если ошибка повторяется, проверьте настройки OpenRouter API.';
                } else if (errorMsg.includes('api key') || errorMsg.includes('unauthorized') || errorMsg.includes('401')) {
                    errorMessage += 'Ошибка авторизации в OpenRouter API. Проверьте OPENROUTER_API_KEY в config.env';
                } else {
                    // Извлекаем детали после "status: 500" или используем полное сообщение
                    const details = errorMsg.includes('status: 500') 
                        ? errorMsg.split('status: 500')[1].trim() 
                        : errorMsg;
                    errorMessage += details || 'Внутренняя ошибка сервера. Проверьте логи сервиса.';
                }
            } else if (errorMsg.includes('status: 504') || errorMsg.includes('Превышено время ожидания')) {
                errorMessage += 'Превышено время ожидания. Генерация описания может занять до 90 секунд. Попробуйте еще раз.';
            } else if (errorMsg.includes('status: 401')) {
                errorMessage += 'Ошибка авторизации в OpenRouter API. Проверьте OPENROUTER_API_KEY в config.env';
            } else if (errorMsg.includes('status: 404')) {
                errorMessage += 'Товар не найден в каталоге. Убедитесь, что товар существует.';
            } else {
                // Используем сообщение напрямую, если оно уже содержит детали от сервиса
                errorMessage = errorMsg.startsWith('Ошибка при генерации описания:') 
                    ? errorMsg 
                    : errorMessage + errorMsg;
            }
            
            showMessage(errorMessage, 'error');
        })
        .finally(() => {
            // Восстанавливаем кнопку
            target.disabled = false;
            target.textContent = 'AI-описание';
        });
        
        return;
    }
    
    // Обработка кнопки "Удалить"
    if (target.classList.contains('delete-btn')) {
        const productId = target.getAttribute('data-id');
        
        if (!confirm('Вы уверены, что хотите удалить этот товар?')) {
            return;
        }
        
        try {
            // Удаляем товар из локального массива
            products = products.filter(p => p.id != productId);
            saveProducts();
            renderProducts();
            showMessage('Товар успешно удален!', 'success');
            
        } catch (error) {
            console.error('Ошибка при удалении товара:', error);
            showMessage('Ошибка при удалении товара: ' + error.message);
        }
    }
    
    // Обработка кнопки "Редактировать"
    if (target.classList.contains('edit-btn')) {
        const productId = target.getAttribute('data-id');
        
        try {
            // Находим товар в локальном массиве
            const product = products.find(p => p.id == productId);
            if (product) {
                fillFormWithProduct(product);
                // Прокручиваем к форме
                productForm.scrollIntoView({ behavior: 'smooth' });
            }
            
        } catch (error) {
            console.error('Ошибка при загрузке товара для редактирования:', error);
            showMessage('Ошибка при загрузке товара: ' + error.message);
        }
    }
});

// Функция для получения описания промпта
function getPromptDescription(promptId) {
    const descriptions = {
        'recommendation_prompt': 'Промпт для генерации рекомендаций виниловых пластинок',
        'description_prompt': 'Промпт для генерации описаний виниловых пластинок'
    };
    return descriptions[promptId] || 'Промпт для AI';
}

// Функция для загрузки и отображения промптов
async function fetchAndRenderPrompts() {
    const promptsList = document.getElementById('prompts-list');
    if (!promptsList) return;
    
    try {
        // Показываем индикатор загрузки
        promptsList.innerHTML = '<div style="text-align: center; color: #666; padding: 20px;">Загрузка промптов...</div>';
        
        // GET-запрос на prompts-manager
        const promptsManagerUrl = window.API_CONFIG?.promptsManager || 'http://localhost:8007';
        const response = await fetch(`${promptsManagerUrl}/api/v1/prompts`);
        
        if (!response.ok) {
            // Пытаемся получить детали ошибки из ответа
            let errorDetail = '';
            try {
                const errorData = await response.json();
                errorDetail = errorData.detail || errorData.message || '';
            } catch (e) {
                errorDetail = response.statusText || '';
            }
            
            const errorMessage = response.status === 500
                ? `Внутренняя ошибка сервера (500). ${errorDetail ? `Детали: ${errorDetail}` : 'Проверьте логи сервиса prompts-manager.'}`
                : `HTTP error! status: ${response.status}${errorDetail ? ` - ${errorDetail}` : ''}`;
            
            throw new Error(errorMessage);
        }
        
        const prompts = await response.json();
        
        if (!prompts || prompts.length === 0) {
            promptsList.innerHTML = `
                <div style="text-align: center; color: #d32f2f; padding: 20px; background: #2a1a1a; border-radius: 8px; border: 1px solid #d32f2f;">
                    <strong style="font-size: 18px; display: block; margin-bottom: 10px;">⚠️ Промпты не найдены</strong>
                    <p style="color: #b0b0b0; margin: 10px 0;">База данных пуста. Промпты должны создаваться автоматически при первом запуске сервиса prompts-manager.</p>
                    <div style="margin-top: 15px; padding: 15px; background: #1a1a1a; border-radius: 5px; text-align: left;">
                        <strong style="color: #ff6b35; display: block; margin-bottom: 10px;">📋 Решение:</strong>
                        <ol style="margin: 0; padding-left: 20px; color: #b0b0b0; line-height: 1.8;">
                            <li>Убедитесь, что сервис prompts-manager запущен</li>
                            <li>Перезапустите сервис: <code style="background: #2a2a2a; padding: 2px 6px; border-radius: 3px;">python start_services_final.py</code></li>
                            <li>Проверьте логи сервиса на наличие ошибок при создании промптов</li>
                            <li>Нажмите кнопку "Попробовать снова" ниже</li>
                        </ol>
                    </div>
                    <button onclick="fetchAndRenderPrompts()" style="margin-top: 15px; padding: 10px 20px; background: #667eea; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: 600; transition: opacity 0.3s;">
                        🔄 Попробовать снова
                    </button>
                </div>
            `;
            showMessage('Промпты не найдены в базе данных. Проверьте, что сервис prompts-manager запущен и создал дефолтные промпты.', 'error');
            return;
        }
        
        // Очищаем контейнер
        promptsList.innerHTML = '';
        
        // Создаем карточку для каждого промпта
        prompts.forEach(prompt => {
            const card = document.createElement('div');
            card.style.cssText = 'background: #1a1a1a; padding: 20px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #333; position: relative;';
            
            // Заголовок карточки
            const headerDiv = document.createElement('div');
            headerDiv.style.cssText = 'margin-bottom: 15px; padding-right: 100px;';
            
            const nameLabel = document.createElement('div');
            nameLabel.textContent = prompt.name || prompt.id;
            nameLabel.style.cssText = 'color: #ff6b35; font-weight: 600; font-size: 18px; margin-bottom: 5px;';
            headerDiv.appendChild(nameLabel);
            
            // Описание промпта (если есть)
            const descriptionDiv = document.createElement('div');
            descriptionDiv.textContent = getPromptDescription(prompt.id);
            descriptionDiv.style.cssText = 'color: #b0b0b0; font-size: 14px;';
            headerDiv.appendChild(descriptionDiv);
            
            card.appendChild(headerDiv);
            
            // Метка для textarea
            const contentLabel = document.createElement('label');
            contentLabel.textContent = 'Содержимое промпта:';
            contentLabel.style.cssText = 'display: block; color: #e0e0e0; font-weight: 600; margin-bottom: 10px; font-size: 14px;';
            card.appendChild(contentLabel);
            
            const textarea = document.createElement('textarea');
            textarea.value = prompt.template || '';
            textarea.style.cssText = 'width: 100%; min-height: 200px; padding: 15px; border: 2px solid #333; border-radius: 8px; background: #2a2a2a; color: #e0e0e0; font-size: 14px; font-family: monospace; resize: vertical; box-sizing: border-box; transition: border-color 0.3s;';
            textarea.id = `prompt-textarea-${prompt.id}`;
            textarea.readOnly = true; // По умолчанию только чтение
            
            // Сохраняем оригинальный контент для отслеживания изменений
            let originalContent = prompt.template || '';
            
            // Отслеживание изменений в textarea (только если редактируется)
            textarea.addEventListener('input', () => {
                if (!textarea.readOnly) {
                    const currentContent = textarea.value.trim();
                    if (currentContent !== originalContent) {
                        textarea.style.borderColor = '#ff6b35';
                    } else {
                        textarea.style.borderColor = '#333';
                    }
                }
            });
            
            card.appendChild(textarea);
            
            // Контейнер для кнопок
            const buttonsContainer = document.createElement('div');
            buttonsContainer.style.cssText = 'margin-top: 15px; display: flex; gap: 10px; align-items: center; flex-wrap: wrap;';
            
            const editBtn = document.createElement('button');
            editBtn.textContent = 'Редактировать';
            editBtn.style.cssText = 'padding: 10px 20px; background: linear-gradient(135deg, #ff6b35 0%, #ff8e53 100%); color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; font-weight: 600; transition: opacity 0.3s;';
            
            const saveBtn = document.createElement('button');
            saveBtn.textContent = 'Сохранить';
            saveBtn.style.cssText = 'padding: 10px 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; font-weight: 600; transition: opacity 0.3s; display: none;';
            
            // Кнопка "Редактировать"
            editBtn.addEventListener('click', () => {
                textarea.readOnly = false;
                textarea.style.borderColor = '#ff6b35';
                editBtn.style.display = 'none';
                saveBtn.style.display = 'inline-block';
                originalContent = textarea.value; // Обновляем оригинальный контент при начале редактирования
            });
            
            // Кнопка "Сохранить"
            saveBtn.addEventListener('click', async () => {
                const newContent = textarea.value.trim();
                
                if (!newContent) {
                    showMessage('Промпт не может быть пустым', 'error');
                    return;
                }
                
                try {
                    // Отключаем кнопку на время запроса
                    saveBtn.disabled = true;
                    saveBtn.textContent = 'Сохранение...';
                    saveBtn.style.opacity = '0.6';
                    
                    // PUT-запрос для обновления промпта
                    const promptsManagerUrl = window.API_CONFIG?.promptsManager || 'http://localhost:8007';
                    const updateResponse = await fetch(`${promptsManagerUrl}/api/v1/prompts/${prompt.id}`, {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            template: newContent
                        })
                    });
                    
                    if (!updateResponse.ok) {
                        let errorMessage = 'Неизвестная ошибка';
                        try {
                            const errorData = await updateResponse.json();
                            errorMessage = errorData.detail || errorData.message || `HTTP ${updateResponse.status}`;
                        } catch (e) {
                            errorMessage = `HTTP error! status: ${updateResponse.status}`;
                        }
                        throw new Error(errorMessage);
                    }
                    
                    const updatedPrompt = await updateResponse.json();
                    
                    // Обновляем оригинальный контент после успешного сохранения
                    textarea.value = updatedPrompt.template;
                    textarea.style.borderColor = '#333';
                    originalContent = updatedPrompt.template;
                    textarea.readOnly = true;
                    
                    // Скрываем кнопку сохранения и показываем редактирование
                    saveBtn.style.display = 'none';
                    editBtn.style.display = 'inline-block';
                    
                    showMessage(`Промпт "${prompt.name || prompt.id}" успешно сохранен!`, 'success');
                    
                } catch (error) {
                    console.error('Ошибка при сохранении промпта:', error);
                    
                    // Улучшенная обработка различных типов ошибок
                    let errorMessage = error.message;
                    
                    if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
                        errorMessage = 'Не удалось подключиться к сервису. Проверьте, что prompts-manager запущен на порту 8007.';
                    } else if (error.message.includes('timeout') || error.message.includes('aborted')) {
                        errorMessage = 'Превышено время ожидания. Попробуйте еще раз.';
                    }
                    
                    showMessage('Ошибка при сохранении промпта: ' + errorMessage, 'error');
                } finally {
                    // Восстанавливаем кнопку
                    saveBtn.disabled = false;
                    saveBtn.textContent = 'Сохранить';
                    saveBtn.style.opacity = '1';
                }
            });
            
            buttonsContainer.appendChild(editBtn);
            buttonsContainer.appendChild(saveBtn);
            card.appendChild(buttonsContainer);
            
            // Информация внизу карточки
            const footerDiv = document.createElement('div');
            footerDiv.style.cssText = 'margin-top: 15px; padding-top: 15px; border-top: 1px solid #333; color: #666; font-size: 12px;';
            footerDiv.textContent = `ID: ${prompt.id}`;
            card.appendChild(footerDiv);
            
            promptsList.appendChild(card);
        });
        
    } catch (error) {
        console.error('Ошибка при загрузке промптов:', error);
        
        // Улучшенная обработка ошибок сети
        let errorMessage = error.message;
        let detailedMessage = '';
        
        if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError') || error.message.includes('ERR_CONNECTION_REFUSED')) {
            errorMessage = 'Сервис prompts-manager не запущен';
            detailedMessage = `
                <div style="margin-top: 15px; padding: 15px; background: #1a1a1a; border-radius: 5px; text-align: left;">
                    <strong style="color: #ff6b35; display: block; margin-bottom: 10px;">📋 Как запустить сервис:</strong>
                    <ol style="margin: 0; padding-left: 20px; color: #b0b0b0; line-height: 1.8;">
                        <li>Откройте терминал в корне проекта</li>
                        <li>Запустите: <code style="background: #2a2a2a; padding: 2px 6px; border-radius: 3px;">python start_services_final.py</code></li>
                        <li>Или отдельно: <code style="background: #2a2a2a; padding: 2px 6px; border-radius: 3px;">start_prompts_manager.bat</code></li>
                        <li>Дождитесь сообщения "База данных инициализирована успешно" и "✅ Дефолтные промпты проверены/созданы успешно"</li>
                        <li>Если есть ошибки, проверьте логи в папке <code style="background: #2a2a2a; padding: 2px 6px; border-radius: 3px;">logs/prompts-manager_stderr.log</code></li>
                        <li>Нажмите кнопку "Попробовать снова" ниже</li>
                    </ol>
                    <p style="color: #b0b0b0; margin-top: 10px;"><strong>Примечание:</strong> Сервис должен быть запущен на порту 8007. Проверьте, что порт не занят другим приложением.</p>
                </div>
            `;
        } else if (error.message.includes('timeout') || error.message.includes('aborted')) {
            errorMessage = 'Превышено время ожидания';
            detailedMessage = 'Сервер не отвечает. Проверьте доступность сервиса.';
        } else if (error.message.includes('500') || error.message.includes('Internal Server Error')) {
            errorMessage = 'Внутренняя ошибка сервера (500)';
            detailedMessage = `
                <div style="margin-top: 15px; padding: 15px; background: #1a1a1a; border-radius: 5px; text-align: left;">
                    <strong style="color: #ff6b35; display: block; margin-bottom: 10px;">⚠️ Ошибка 500:</strong>
                    <p style="color: #b0b0b0; margin: 5px 0;">Сервер prompts-manager вернул ошибку 500. Это может быть связано с:</p>
                    <ul style="margin: 10px 0; padding-left: 20px; color: #b0b0b0; line-height: 1.8;">
                        <li>Проблемами с базой данных</li>
                        <li>Ошибками в коде сервиса</li>
                        <li>Проблемами с сериализацией данных</li>
                    </ul>
                    <p style="color: #b0b0b0; margin-top: 10px;"><strong>Решение:</strong> Проверьте логи сервиса prompts-manager в папке logs/ или перезапустите сервис.</p>
                </div>
            `;
        } else {
            detailedMessage = `Детали ошибки: ${error.message}`;
        }
        
        promptsList.innerHTML = `
            <div style="color: #d32f2f; padding: 20px; text-align: center; background: #2a1a1a; border-radius: 8px; border: 1px solid #d32f2f;">
                <strong style="font-size: 18px; display: block; margin-bottom: 10px;">❌ Ошибка загрузки промптов</strong>
                <div style="margin: 10px 0; font-weight: 600;">${errorMessage}</div>
                ${detailedMessage ? `<div style="color: #b0b0b0; font-size: 14px; margin-top: 10px;">${detailedMessage}</div>` : ''}
                <button onclick="fetchAndRenderPrompts()" style="margin-top: 15px; padding: 10px 20px; background: #667eea; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: 600; transition: opacity 0.3s;">
                    🔄 Попробовать снова
                </button>
            </div>
        `;
        showMessage('Ошибка при загрузке промптов: ' + errorMessage, 'error');
    }
}

// Обработчик для кнопки генерации AI-рекомендаций
document.addEventListener('DOMContentLoaded', () => {
    loadProducts();
    fetchAndRenderPrompts();
    
    // Добавляем обработчик для кнопки генерации рекомендаций
    const generateBtn = document.getElementById('generate-btn');
    const aiPrompt = document.getElementById('ai-prompt');
    const aiResult = document.getElementById('ai-result');
    
    if (generateBtn && aiPrompt && aiResult) {
        generateBtn.addEventListener('click', async () => {
            const prompt = aiPrompt.value.trim();
            
            if (!prompt) {
                showMessage('Пожалуйста, введите запрос для AI-рекомендаций', 'error');
                return;
            }
            
            try {
                // Показываем индикатор загрузки
                generateBtn.disabled = true;
                generateBtn.textContent = 'Генерация...';
                aiResult.style.display = 'block';
                aiResult.innerHTML = '<div style="text-align: center; color: #666;">Генерация рекомендаций...</div>';
                
                // Отправляем POST запрос к API рекомендаций
                const recommenderUrl = window.API_CONFIG?.recommender || 'http://localhost:8004';
                const response = await fetch(`${recommenderUrl}/api/v1/recommendations/generate`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        user_preferences: prompt,
                        max_recommendations: 6,
                        model: 'gpt-4'
                    })
                });
                
                if (!response.ok) {
                    // Извлекаем детали ошибки из ответа сервера
                    let errorDetail = '';
                    try {
                        const errorData = await response.json();
                        errorDetail = errorData.detail || errorData.message || '';
                    } catch (e) {
                        errorDetail = response.statusText || `HTTP ${response.status}`;
                    }
                    
                    // Формируем понятное сообщение об ошибке
                    let errorMessage = errorDetail || `HTTP error! status: ${response.status}`;
                    
                    // Добавляем специфичные сообщения для разных статусов
                    if (response.status === 502) {
                        errorMessage = `Ошибка при обращении к внешнему AI сервису: ${errorDetail}`;
                    } else if (response.status === 500) {
                        errorMessage = errorDetail || 'Внутренняя ошибка сервиса рекомендаций';
                    } else if (response.status === 504) {
                        errorMessage = 'Превышено время ожидания генерации (90 сек). Попробуйте позже.';
                    } else if (response.status === 401) {
                        errorMessage = 'Ошибка авторизации в OpenRouter API. Проверьте OPENROUTER_API_KEY в config.env';
                    }
                    
                    throw new Error(errorMessage);
                }
                
                const data = await response.json();
                
                // Отображаем результат в красивом формате
                let resultHtml = `
                    <div style="background: #1a1a1a; padding: 20px; border-radius: 8px; margin: 10px 0;">
                        <h3 style="color: #ff6b35; margin-bottom: 15px;">Результат AI-анализа:</h3>
                        <p style="color: #e0e0e0; margin-bottom: 20px;">
                            <strong>Модель:</strong> ${data.model || 'gpt-4'} | 
                            <strong>Проанализировано пластинок:</strong> ${data.recommendations ? data.recommendations.length : 0}
                        </p>
                        
                        <h3 style="color: #ff6b35; margin-bottom: 15px;">Рекомендации:</h3>
                `;
                
                if (data.recommendations && data.recommendations.length > 0) {
                    resultHtml += '<ul style="color: #e0e0e0; line-height: 1.6;">';
                    data.recommendations.forEach((book, index) => {
                        resultHtml += `
                            <li style="margin-bottom: 15px;">
                                <strong style="color: #ff6b35;">${book.title || book.name} (id: ${book.id})</strong><br>
                                <span style="color: #b0b0b0; font-size: 14px;">${book.reasoning || 'Рекомендация основана на ваших предпочтениях'}</span>
                            </li>
                        `;
                    });
                    resultHtml += '</ul>';
                } else {
                    resultHtml += '<p style="color: #b0b0b0;">Рекомендации не найдены</p>';
                }
                
                if (data.reasoning) {
                    resultHtml += `
                        <div style="margin-top: 20px; padding: 15px; background: #2a2a2a; border-radius: 5px;">
                            <h4 style="color: #ff6b35; margin-bottom: 10px;">Объяснение логики рекомендаций:</h4>
                            <p style="color: #b0b0b0; line-height: 1.5;">${data.reasoning}</p>
                        </div>
                    `;
                }
                
                resultHtml += '</div>';
                aiResult.innerHTML = resultHtml;
                
                showMessage('AI-рекомендации успешно сгенерированы!', 'success');
                
            } catch (error) {
                console.error('Ошибка при генерации рекомендаций:', error);
                const errorMessage = error.message || 'Неизвестная ошибка при генерации рекомендаций';
                aiResult.innerHTML = `
                    <div style="color: #d32f2f; padding: 15px; background: #2a1a1a; border-radius: 5px;">
                        <strong>❌ Ошибка при генерации рекомендаций:</strong>
                        <br><br>${errorMessage}
                        <br><br>Проверьте, что сервис рекомендаций запущен на порту 8004 и OPENROUTER_API_KEY настроен корректно.
                    </div>
                `;
                showMessage('Ошибка при генерации рекомендаций: ' + errorMessage, 'error');
            } finally {
                // Восстанавливаем кнопку
                generateBtn.disabled = false;
                generateBtn.textContent = 'Сгенерировать рекомендации';
                generateBtn.style.transform = 'translateY(0)';
                generateBtn.style.boxShadow = 'none';
            }
        });
    }
});

// Генерация описания для товара в форме редактирования
async function generateDescription() {
    const editingId = productForm.getAttribute('data-editing-id');
    
    if (!editingId) {
        showMessage('Сначала откройте товар для редактирования, затем нажмите кнопку генерации', 'error');
        return;
    }
    
    const descriptionTextarea = document.getElementById('description');
    const generateBtn = document.getElementById('generate-description-btn');
    const statusDiv = document.getElementById('description-status');
    
    generateBtn.disabled = true;
    generateBtn.textContent = '⏳ Генерация...';
    statusDiv.textContent = '🔄 Генерация описания через AI... (это может занять 30-90 сек)';
    statusDiv.style.color = '#007bff';
    
    // Добавляем индикатор прогресса
    let progressDots = 0;
    const progressInterval = setInterval(() => {
        progressDots = (progressDots + 1) % 4;
        const dots = '.'.repeat(progressDots) + ' '.repeat(3 - progressDots);
        statusDiv.textContent = `🔄 Генерация описания через AI${dots} (это может занять 30-90 сек)`;
    }, 500);
    
    try {
        // Создаем AbortController для таймаута (100 секунд для LLM запросов)
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 100000); // 100 секунд
        
        const recommenderUrl = window.API_CONFIG?.recommender || 'http://localhost:8004';
        const response = await fetch(`${recommenderUrl}/api/v1/recommendations/generate-description/${editingId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            signal: controller.signal
        });
        
        if (!response.ok) {
            // Извлекаем детали ошибки из ответа сервера
            let errorDetail = '';
            try {
                const errorData = await response.json();
                errorDetail = errorData.detail || errorData.message || '';
            } catch (e) {
                errorDetail = response.statusText || `HTTP ${response.status}`;
            }
            
            // Формируем понятное сообщение об ошибке
            let errorMessage = errorDetail || `HTTP error! status: ${response.status}`;
            
            // Добавляем специфичные сообщения для разных статусов
            if (response.status === 502) {
                errorMessage = `Ошибка при обращении к внешнему AI сервису: ${errorDetail}`;
            } else if (response.status === 500) {
                errorMessage = errorDetail || 'Внутренняя ошибка сервиса рекомендаций';
            } else if (response.status === 504) {
                errorMessage = 'Превышено время ожидания генерации (90 сек). Попробуйте позже.';
            } else if (response.status === 401) {
                errorMessage = 'Ошибка авторизации в OpenRouter API. Проверьте OPENROUTER_API_KEY в config.env';
            } else if (response.status === 404) {
                errorMessage = `Товар не найден: ${errorDetail}`;
            }
            
            throw new Error(errorMessage);
        }
        
        const data = await response.json();
        
        clearTimeout(timeoutId);
        clearInterval(progressInterval);
        
        if (data.success && data.generated_description) {
            descriptionTextarea.value = data.generated_description;
            statusDiv.textContent = '✅ Описание успешно сгенерировано!';
            statusDiv.style.color = '#28a745';
            showMessage('Описание успешно сгенерировано через AI!', 'success');
        } else {
            throw new Error(data.message || 'Не удалось получить описание');
        }
    } catch (error) {
        if (error.name === 'AbortError') {
            statusDiv.textContent = '❌ Превышено время ожидания (~100 сек)';
            statusDiv.style.color = '#dc3545';
            showMessage('Время ожидания генерации истекло. Проверьте подключение к интернету и попробуйте еще раз.', 'error');
        } else {
            console.error('Ошибка генерации описания:', error);
            const errorMessage = error.message || 'Неизвестная ошибка при генерации описания';
            statusDiv.textContent = '❌ Ошибка: ' + errorMessage;
            statusDiv.style.color = '#dc3545';
            showMessage('Ошибка при генерации описания: ' + errorMessage, 'error');
        }
    } finally {
        // Гарантируем очистку всех таймеров
        if (typeof timeoutId !== 'undefined') clearTimeout(timeoutId);
        if (typeof progressInterval !== 'undefined') clearInterval(progressInterval);
        generateBtn.disabled = false;
        generateBtn.innerHTML = '🤖 AI Генератор';
    }
}

// Генерация описания для товара из таблицы
async function generateDescriptionForProduct(productId) {
    if (!confirm(`Сгенерировать новое AI-описание для товара ID ${productId}? Текущее описание будет заменено в каталоге.`)) {
        return;
    }
    
    // Показываем индикатор прогресса
    showMessage('🔄 Генерация описания... Это может занять 30-90 секунд', 'success');
    
    try {
        // Создаем AbortController для таймаута (100 секунд для LLM запросов)
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 100000); // 100 секунд
        
        const recommenderUrl = window.API_CONFIG?.recommender || 'http://localhost:8004';
        const response = await fetch(`${recommenderUrl}/api/v1/recommendations/generate-description/${productId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
            // Извлекаем детали ошибки из ответа сервера
            let errorDetail = '';
            try {
                const errorData = await response.json();
                errorDetail = errorData.detail || errorData.message || '';
            } catch (e) {
                errorDetail = response.statusText || `HTTP ${response.status}`;
            }
            
            // Формируем понятное сообщение об ошибке
            let errorMessage = errorDetail || `HTTP error! status: ${response.status}`;
            
            // Добавляем специфичные сообщения для разных статусов
            if (response.status === 502) {
                errorMessage = `Ошибка при обращении к внешнему AI сервису: ${errorDetail}`;
            } else if (response.status === 500) {
                errorMessage = errorDetail || 'Внутренняя ошибка сервиса рекомендаций';
            } else if (response.status === 504) {
                errorMessage = 'Превышено время ожидания генерации (90 сек). Попробуйте позже.';
            } else if (response.status === 401) {
                errorMessage = 'Ошибка авторизации в OpenRouter API. Проверьте OPENROUTER_API_KEY в config.env';
            } else if (response.status === 404) {
                errorMessage = `Товар не найден: ${errorDetail}`;
            }
            
            throw new Error(errorMessage);
        }
        
        const data = await response.json();
        
        if (data.success && data.generated_description) {
            // Обновляем описание в локальном хранилище
            const product = products.find(p => p.id == productId);
            if (product) {
                product.description = data.generated_description;
                saveProducts();
                renderProducts();
            }
            showMessage(`✅ Описание для товара ID ${productId} успешно сгенерировано!`, 'success');
        } else {
            throw new Error(data.message || 'Не удалось получить описание');
        }
    } catch (error) {
        if (error.name === 'AbortError') {
            showMessage('❌ Время ожидания генерации истекло (~100 сек). Проверьте подключение к интернету и попробуйте еще раз.', 'error');
        } else {
            console.error('Ошибка генерации описания:', error);
            const errorMessage = error.message || 'Неизвестная ошибка при генерации описания';
            showMessage('❌ Ошибка при генерации описания: ' + errorMessage, 'error');
        }
    }
}
