// Обработка модального окна рекомендаций
document.addEventListener('DOMContentLoaded', function() {
    const recommendationsBtn = document.getElementById('get-recommendations');
    const modal = document.getElementById('recommendations-modal');
    const closeBtn = document.getElementById('close-recommendations');
    const generateBtn = document.getElementById('generate-recommendations');
    const loadingIndicator = document.getElementById('loading-indicator');
    const recommendationsResult = document.getElementById('recommendations-result');
    const recommendationsContent = document.getElementById('recommendations-content');

    // Проверяем, что все элементы существуют
    if (!recommendationsBtn || !modal || !closeBtn || !generateBtn) {
        console.warn('Некоторые элементы рекомендаций не найдены');
        return;
    }

    // Открытие модального окна
    recommendationsBtn.addEventListener('click', function(e) {
        e.preventDefault();
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden'; // Блокируем скролл
    });

    // Закрытие модального окна
    closeBtn.addEventListener('click', function() {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
        resetForm();
    });

    // Закрытие по клику вне модального окна
    window.addEventListener('click', function(e) {
        if (e.target === modal) {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto';
            resetForm();
        }
    });

    // Закрытие по Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && modal.style.display === 'block') {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto';
            resetForm();
        }
    });

    // Генерация рекомендаций
    generateBtn.addEventListener('click', function() {
        generateRecommendations();
    });

    // Сброс формы
    function resetForm() {
        document.getElementById('user-preferences').value = '';
        const currentBooksInput = document.getElementById('current-books') || document.getElementById('current-records');
        if (currentBooksInput) currentBooksInput.value = '';
        document.getElementById('genre-preferences').value = '';
        document.getElementById('ai-model').value = 'gpt-4';
        document.getElementById('max-recommendations').value = '5';
        recommendationsResult.style.display = 'none';
        recommendationsContent.innerHTML = '';
    }

    // Генерация рекомендаций
    async function generateRecommendations() {
        const userPreferences = document.getElementById('user-preferences').value;
        const currentBooksInput = document.getElementById('current-books') || document.getElementById('current-records');
        const currentBooks = currentBooksInput ? currentBooksInput.value : '';
        const genrePreferences = document.getElementById('genre-preferences').value;
        const aiModel = document.getElementById('ai-model').value;
        const maxRecommendations = parseInt(document.getElementById('max-recommendations').value);

        // Показываем индикатор загрузки
        recommendationsResult.style.display = 'block';
        loadingIndicator.style.display = 'block';
        recommendationsContent.innerHTML = '';
        generateBtn.disabled = true;
        generateBtn.textContent = 'Генерируем...';

        try {
            // Подготавливаем данные запроса
            const requestData = {
                user_preferences: userPreferences || null,
                current_books: currentBooks && currentBooks.trim() 
                    ? currentBooks.split(',').map(id => parseInt(id.trim())).filter(id => !isNaN(id))
                    : null, // Используем current_books для обратной совместимости с API
                genre_preferences: genrePreferences && genrePreferences.trim()
                    ? genrePreferences.split(',').map(genre => genre.trim())
                    : null,
                max_recommendations: maxRecommendations,
                model: aiModel
            };

            console.log('Отправляем запрос:', requestData);

            // Отправляем запрос к сервису рекомендаций
            const response = await fetch('http://127.0.0.1:8004/api/v1/recommendations/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });

            console.log('Ответ сервера:', response.status);

            if (!response.ok) {
                const errorData = await response.text();
                throw new Error(`HTTP error! status: ${response.status}, details: ${errorData}`);
            }

            const data = await response.json();
            console.log('Данные ответа:', data);

            // Скрываем индикатор загрузки
            loadingIndicator.style.display = 'none';

            // Отображаем результаты
            displayRecommendations(data);

        } catch (error) {
            console.error('Ошибка при получении рекомендаций:', error);
            
            // Скрываем индикатор загрузки
            loadingIndicator.style.display = 'none';
            
            // Показываем ошибку
            recommendationsContent.innerHTML = `
                <div class="error-message">
                    <h4>❌ Ошибка при получении рекомендаций</h4>
                    <p><strong>Детали:</strong> ${error.message}</p>
                    <p><strong>Возможные причины:</strong></p>
                    <ul>
                        <li>Сервис рекомендаций не запущен (порт 8004)</li>
                        <li>Сервис каталога не запущен (порт 8000)</li>
                        <li>Не настроен OPENROUTER_API_KEY</li>
                        <li>Проблемы с сетью</li>
                    </ul>
                    <p><strong>Попробуйте:</strong></p>
                    <ul>
                        <li>Запустить сервисы: <code>start_all_services.bat</code></li>
                        <li>Проверить подключение к интернету</li>
                        <li>Попробовать другую AI-модель</li>
                    </ul>
                </div>
            `;
        } finally {
            // Восстанавливаем кнопку
            generateBtn.disabled = false;
            generateBtn.textContent = 'Получить рекомендации';
        }
    }

    // Функция для очистки Markdown символов
    function cleanMarkdown(text) {
        if (!text) return '';
        
        // Убираем все оставшиеся Markdown жирный текст **text** -> text (обрабатываем вложенные случаи)
        let prevText = '';
        while (text !== prevText) {
            prevText = text;
            text = text.replace(/\*\*([^*]+)\*\*/g, '$1');
        }
        
        // Убираем одиночные звездочки *text* -> text (но не внутри **text**)
        text = text.replace(/(?<!\*)\*([^*]+?)\*(?!\*)/g, '$1');
        
        // Убираем заголовки ### (в начале строки и в середине текста)
        text = text.replace(/#{1,6}\s+/g, '');
        
        // Убираем markdown списки - * + (в начале строки)
        text = text.replace(/^[\s]*[-*+]\s+/gm, '');
        
        // Убираем нумерованные списки типа "1. ", "2. " и т.д.
        text = text.replace(/^\d+\.\s+/gm, '');
        
        // Убираем специальные кавычки, заменяем на обычные
        text = text.replace(/[""\u201C\u201D\u201E\u201F\u2033\u2036]/g, '"');
        
        // Убираем оставшиеся одиночные звездочки и множественные
        text = text.replace(/\*+/g, '');
        
        // Разбиваем на строки и очищаем
        const lines = text.split('\n').map(line => line.trim()).filter(line => line.length > 0);
        text = lines.join('\n');
        
        // Убираем множественные переносы строк (более 2 подряд заменяем на 2)
        text = text.replace(/\n{3,}/g, '\n\n');
        
        // Убираем множественные пробелы (более 1 подряд)
        text = text.replace(/ +/g, ' ');
        
        return text.trim();
    }
    
    // Функция для экранирования HTML
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Отображение результатов рекомендаций
    function displayRecommendations(data) {
        // Очищаем reasoning от Markdown
        const cleanReasoning = cleanMarkdown(data.reasoning || '');
        
        let html = `
            <div class="success-message">
                <h4>🎯 Ваши персональные рекомендации готовы!</h4>
                <p><strong>Уверенность AI:</strong> <span class="confidence-score">${(data.confidence_score * 100).toFixed(1)}%</span></p>
                <p><strong>Обоснование:</strong></p>
                <div style="color: #B0B0B0; font-size: 14px; line-height: 1.8; margin-top: 12px; padding: 16px; background: rgba(255, 255, 255, 0.03); border-radius: 8px; white-space: pre-wrap; word-wrap: break-word;">${escapeHtml(cleanReasoning)}</div>
            </div>
        `;

        if (data.recommendations && data.recommendations.length > 0) {
            html += '<h4 style="color: #EAEAEA; margin: 20px 0 15px 0;">💿 Рекомендуемые пластинки:</h4>';
            
            data.recommendations.forEach((rec, index) => {
                const artist = rec.artist || rec.author || 'Неизвестный исполнитель';
                html += `
                    <div class="recommendation-item">
                        <h4>${index + 1}. ${rec.name || 'Неизвестная пластинка'}</h4>
                        <p><strong>Исполнитель:</strong> ${artist}</p>
                        <p><strong>Почему рекомендую:</strong> ${rec.reason || 'Подходит под ваши предпочтения'}</p>
                        ${rec.match_score ? `<p><strong>Совпадение:</strong> <span class="match-score">${(rec.match_score * 100).toFixed(1)}%</span></p>` : ''}
                    </div>
                `;
            });
        } else {
            html += '<p style="color: #B0B0B0; text-align: center; padding: 20px;">😔 К сожалению, не удалось сгенерировать рекомендации. Попробуйте изменить параметры запроса.</p>';
        }

        recommendationsContent.innerHTML = html;
    }

    // Проверка состояния сервисов при загрузке
    async function checkServicesStatus() {
        try {
            // Проверяем каталог
            const catalogUrl = window.API_CONFIG?.catalog || 'http://localhost:8000';
            const catalogResponse = await fetch(`${catalogUrl}/health`);
            const catalogOk = catalogResponse.ok;
            
            // Проверяем рекомендации
            let recommendationsOk = false;
            try {
                const recommenderUrl = window.API_CONFIG?.recommender || 'http://localhost:8004';
                const recResponse = await fetch(`${recommenderUrl}/health`);
                recommendationsOk = recResponse.ok;
            } catch (e) {
                recommendationsOk = false;
            }

            if (!catalogOk || !recommendationsOk) {
                console.warn('Некоторые сервисы недоступны:', {
                    catalog: catalogOk,
                    recommendations: recommendationsOk
                });
            }
        } catch (error) {
            console.warn('Ошибка при проверке сервисов:', error);
        }
    }

    // Проверяем состояние сервисов при загрузке
    checkServicesStatus();
});
