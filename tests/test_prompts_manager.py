#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тесты для сервиса prompts-manager
"""

import pytest
import requests
import time
import sys
import os
from pathlib import Path

# Добавляем корневую директорию в путь
root_path = Path(__file__).parent.parent
sys.path.insert(0, str(root_path))

# Базовый URL сервиса
BASE_URL = "http://127.0.0.1:8007"

class TestPromptsManager:
    """Тесты для сервиса prompts-manager"""
    
    @classmethod
    def setup_class(cls):
        """Проверка доступности сервиса перед тестами"""
        max_retries = 10
        for i in range(max_retries):
            try:
                response = requests.get(f"{BASE_URL}/health", timeout=2)
                if response.status_code == 200:
                    print(f"✅ Сервис prompts-manager доступен")
                    return
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)
        
        pytest.skip("Сервис prompts-manager недоступен. Убедитесь, что он запущен на порту 8007.")
    
    def test_health_check(self):
        """Тест health check эндпоинта"""
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "prompts-manager"
    
    def test_get_all_prompts(self):
        """Тест получения списка всех промптов"""
        response = requests.get(f"{BASE_URL}/api/v1/prompts", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Должны существовать дефолтные промпты
        prompt_names = [p["name"] for p in data]
        assert "recommendation_prompt" in prompt_names
        assert "description_prompt" in prompt_names
    
    def test_get_recommendation_prompt(self):
        """Тест получения промпта рекомендаций"""
        response = requests.get(f"{BASE_URL}/api/v1/prompts/recommendation_prompt", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "recommendation_prompt"
        assert "content" in data
        assert len(data["content"]) > 0
        assert "id" in data
        assert "created_at" in data
    
    def test_get_description_prompt(self):
        """Тест получения промпта описаний"""
        response = requests.get(f"{BASE_URL}/api/v1/prompts/description_prompt", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "description_prompt"
        assert "content" in data
        assert len(data["content"]) > 0
        assert "id" in data
        assert "created_at" in data
    
    def test_get_nonexistent_prompt(self):
        """Тест получения несуществующего промпта"""
        response = requests.get(f"{BASE_URL}/api/v1/prompts/nonexistent_prompt", timeout=5)
        assert response.status_code == 404
        data = response.json()
        assert "не найден" in data["detail"]
    
    def test_update_prompt(self):
        """Тест обновления промпта"""
        # Получаем текущий промпт
        response = requests.get(f"{BASE_URL}/api/v1/prompts/recommendation_prompt", timeout=5)
        assert response.status_code == 200
        original_content = response.json()["content"]
        
        # Обновляем промпт
        new_content = "Обновленный тестовый промпт для рекомендаций"
        update_data = {"content": new_content}
        response = requests.put(
            f"{BASE_URL}/api/v1/prompts/recommendation_prompt",
            json=update_data,
            timeout=5
        )
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == new_content
        assert "updated_at" in data
        
        # Проверяем, что updated_at изменился
        assert data["updated_at"] is not None
        
        # Восстанавливаем оригинальный контент
        restore_data = {"content": original_content}
        requests.put(
            f"{BASE_URL}/api/v1/prompts/recommendation_prompt",
            json=restore_data,
            timeout=5
        )
    
    def test_update_nonexistent_prompt(self):
        """Тест обновления несуществующего промпта"""
        update_data = {"content": "Тестовый контент"}
        response = requests.put(
            f"{BASE_URL}/api/v1/prompts/nonexistent_prompt",
            json=update_data,
            timeout=5
        )
        assert response.status_code == 404
        data = response.json()
        assert "не найден" in data["detail"]
    
    def test_update_prompt_validation(self):
        """Тест валидации при обновлении промпта"""
        # Попытка обновить без поля content
        update_data = {}
        response = requests.put(
            f"{BASE_URL}/api/v1/prompts/recommendation_prompt",
            json=update_data,
            timeout=5
        )
        # FastAPI должен вернуть ошибку валидации
        assert response.status_code in [400, 422]
    
    def test_default_prompts_exist(self):
        """Тест проверки существования дефолтных промптов"""
        response = requests.get(f"{BASE_URL}/api/v1/prompts", timeout=5)
        assert response.status_code == 200
        prompts = response.json()
        
        recommendation = next((p for p in prompts if p["name"] == "recommendation_prompt"), None)
        description = next((p for p in prompts if p["name"] == "description_prompt"), None)
        
        assert recommendation is not None, "Промпт recommendation_prompt должен существовать"
        assert description is not None, "Промпт description_prompt должен существовать"
        
        # Проверяем, что контент не пустой
        assert len(recommendation["content"]) > 50, "Контент recommendation_prompt должен быть заполнен"
        assert len(description["content"]) > 50, "Контент description_prompt должен быть заполнен"

if __name__ == "__main__":
    # Запуск тестов через pytest
    pytest.main([__file__, "-v"])

