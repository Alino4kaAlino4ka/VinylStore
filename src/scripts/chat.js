// Модуль для работы с AI-консультантом (чат-бот)
const CHAT_STORAGE_KEY = 'vinyl_shop_chat_history';
const CHAT_API_URL = (window.API_CONFIG?.recommender || 'http://localhost:8004') + '/api/v1/chat/message';

// Инициализация чата при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    initializeChat();
});

function initializeChat() {
    const chatWidget = document.getElementById('chat-widget');
    const chatToggle = document.getElementById('chat-toggle');
    const chatContainer = document.getElementById('chat-container');
    const chatMessages = document.getElementById('chat-messages');
    const chatInput = document.getElementById('chat-input');
    const chatSendBtn = document.getElementById('chat-send-btn');
    const chatClearBtn = document.getElementById('chat-clear-btn');
    const chatCloseBtn = document.getElementById('chat-close-btn');
    
    if (!chatWidget || !chatToggle || !chatContainer || !chatMessages || !chatInput || !chatSendBtn) {
        console.warn('Элементы чата не найдены на странице');
        return;
    }
    
    // Экранирование HTML
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // Форматирование сообщения (подсветка ID пластинок, базовое форматирование)
    function formatMessageContent(content) {
        // Экранируем HTML для безопасности
        let formatted = escapeHtml(content);
        
        // Подсвечиваем упоминания ID пластинок (например: #5, ID 5, пластинка #5)
        formatted = formatted.replace(/(?:пластинка\s*)?#(\d+)|ID\s*(\d+)/gi, '<span class="product-id-highlight">#$1$2</span>');
        
        // Заменяем переносы строк на <br>
        formatted = formatted.replace(/\n/g, '<br>');
        
        return formatted;
    }
    
    // Получение истории из localStorage
    function getChatHistory() {
        try {
            const historyJson = localStorage.getItem(CHAT_STORAGE_KEY);
            if (historyJson) {
                return JSON.parse(historyJson);
            }
        } catch (e) {
            console.error('Ошибка при загрузке истории чата:', e);
        }
        return [];
    }
    
    // Загружаем историю из localStorage
    const history = getChatHistory();
    if (history.length === 0) {
        // Если истории нет, показываем приветственное сообщение (без сохранения в историю)
        const welcomeDiv = document.createElement('div');
        welcomeDiv.className = 'chat-message chat-message-assistant';
        const welcomeContent = document.createElement('div');
        welcomeContent.className = 'chat-message-content';
        welcomeContent.innerHTML = formatMessageContent('Привет! 👋 Я AI-консультант по виниловым пластинкам. Чем могу помочь?');
        welcomeDiv.appendChild(welcomeContent);
        chatMessages.appendChild(welcomeDiv);
    } else {
        // Загружаем историю
        history.forEach(msg => {
            const messageDiv = document.createElement('div');
            messageDiv.className = `chat-message chat-message-${msg.role}`;
            const messageContent = document.createElement('div');
            messageContent.className = 'chat-message-content';
            messageContent.innerHTML = formatMessageContent(msg.content);
            messageDiv.appendChild(messageContent);
            chatMessages.appendChild(messageDiv);
        });
        scrollToBottom();
    }
    
    // Открытие/закрытие чата
    if (chatToggle) {
        chatToggle.addEventListener('click', function() {
            chatContainer.style.display = chatContainer.style.display === 'none' ? 'flex' : 'none';
            if (chatContainer.style.display === 'flex') {
                chatInput.focus();
                scrollToBottom();
            }
        });
    }
    
    if (chatCloseBtn) {
        chatCloseBtn.addEventListener('click', function() {
            chatContainer.style.display = 'none';
        });
    }
    
    // Отправка сообщения
    chatSendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Очистка истории
    if (chatClearBtn) {
        chatClearBtn.addEventListener('click', function() {
            if (confirm('Очистить историю диалога?')) {
                clearChatHistory();
            }
        });
    }
    
    // Функция отправки сообщения
    async function sendMessage() {
        const message = chatInput.value.trim();
        if (!message) {
            // Показываем предупреждение, если сообщение пустое
            chatInput.focus();
            return;
        }
        
        // Добавляем сообщение пользователя в чат
        addMessageToChat('user', message);
        chatInput.value = '';
        
        // Показываем индикатор печати
        showTypingIndicator();
        
        try {
            // Получаем историю диалога
            const history = getChatHistory();
            
            // Получаем ID текущей пластинки (если на странице детализации)
            const urlParams = new URLSearchParams(window.location.search);
            const currentProductId = urlParams.get('id') ? parseInt(urlParams.get('id')) : null;
            
            // Отправляем запрос к API
            const response = await fetch(CHAT_API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    history: history,
                    current_product_id: currentProductId,
                    model: 'gpt-4'
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: 'Ошибка сервера' }));
                throw new Error(errorData.detail || `Ошибка ${response.status}`);
            }
            
            const data = await response.json();
            
            // Убираем индикатор печати
            hideTypingIndicator();
            
            // Добавляем ответ консультанта в чат
            if (data.success && data.response) {
                addMessageToChat('assistant', data.response);
            } else {
                throw new Error('Неверный формат ответа от сервера');
            }
            
        } catch (error) {
            console.error('Ошибка при отправке сообщения:', error);
            hideTypingIndicator();
            addMessageToChat('assistant', `Извините, произошла ошибка: ${error.message}. Пожалуйста, попробуйте позже.`);
        }
    }
    
    // Добавление сообщения в чат
    function addMessageToChat(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message chat-message-${role}`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'chat-message-content';
        messageContent.textContent = content;
        
        // Поддержка простого форматирования (жирный текст, ссылки на ID пластинок)
        messageContent.innerHTML = formatMessageContent(content);
        
        messageDiv.appendChild(messageContent);
        chatMessages.appendChild(messageDiv);
        
        // Сохраняем в историю
        saveMessageToHistory(role, content);
        
        // Прокручиваем вниз
        scrollToBottom();
    }
    
    // Показать индикатор печати
    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.id = 'typing-indicator';
        typingDiv.className = 'chat-message chat-message-assistant';
        typingDiv.innerHTML = '<div class="chat-message-content typing-indicator"><span></span><span></span><span></span></div>';
        chatMessages.appendChild(typingDiv);
        scrollToBottom();
    }
    
    // Скрыть индикатор печати
    function hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    // Прокрутка вниз
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Сохранение сообщения в историю
    function saveMessageToHistory(role, content) {
        const history = getChatHistory();
        history.push({ role, content });
        
        // Ограничиваем историю последними 20 сообщениями
        const limitedHistory = history.slice(-20);
        
        try {
            localStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(limitedHistory));
        } catch (e) {
            console.error('Ошибка при сохранении истории чата:', e);
        }
    }
    
    // Очистка истории
    function clearChatHistory() {
        localStorage.removeItem(CHAT_STORAGE_KEY);
        chatMessages.innerHTML = '';
        // Показываем приветственное сообщение (без сохранения в историю)
        const welcomeDiv = document.createElement('div');
        welcomeDiv.className = 'chat-message chat-message-assistant';
        const welcomeContent = document.createElement('div');
        welcomeContent.className = 'chat-message-content';
        welcomeContent.innerHTML = formatMessageContent('Привет! 👋 Я AI-консультант по виниловым пластинкам. Чем могу помочь?');
        welcomeDiv.appendChild(welcomeContent);
        chatMessages.appendChild(welcomeDiv);
    }
}

// Экспорт функций для использования в других модулях
window.chatModule = {
    sendMessage: function(message) {
        // Функция для программной отправки сообщения
        const chatInput = document.getElementById('chat-input');
        if (chatInput) {
            chatInput.value = message;
            const sendBtn = document.getElementById('chat-send-btn');
            if (sendBtn) {
                sendBtn.click();
            }
        }
    }
};

