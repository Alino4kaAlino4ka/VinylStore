/**
 * Единая конфигурация API для всех frontend компонентов
 * Все порты должны соответствовать config.env
 */

const API_CONFIG = {
    // Основные сервисы
    catalog: 'http://localhost:8000',
    auth: 'http://localhost:8001',
    orders: 'http://localhost:8010',
    users: 'http://localhost:8011',
    recommender: 'http://localhost:8012',
    cart: 'http://localhost:8005',
    promptsManager: 'http://localhost:8007',
    
    // Эндпоинты
    endpoints: {
        // Catalog
        products: '/api/v1/products',
        adminProducts: '/api/v1/admin/products',
        product: (id) => `/api/v1/products/${id}`,
        adminProduct: (id) => `/api/v1/admin/products/${id}`,
        
        // Auth
        register: '/register',
        login: '/token',
        userInfo: '/users/me',
        
        // Orders
        orders: '/api/v1/orders',
        order: (id) => `/api/v1/orders/${id}`,
        
        // Cart
        cart: '/api/v1/cart',
        cartCalculate: '/api/v1/cart/calculate',
        
        // Recommender
        chat: '/api/v1/chat/message',
        recommendations: '/api/v1/recommendations',
        
        // Prompts Manager
        prompts: '/api/v1/prompts',
        prompt: (id) => `/api/v1/prompts/${id}`,
        
        // Health checks
        health: '/health'
    },
    
    // Полные URL для удобства
    getUrl: function(service, endpoint) {
        const baseUrl = this[service];
        if (!baseUrl) {
            console.error(`Service ${service} not found in API_CONFIG`);
            return null;
        }
        return `${baseUrl}${endpoint}`;
    }
};

// Экспорт для использования в других файлах
if (typeof window !== 'undefined') {
    window.API_CONFIG = API_CONFIG;
}
if (typeof module !== 'undefined' && module.exports) {
    module.exports = API_CONFIG;
}

