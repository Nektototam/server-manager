import pytest
from unittest.mock import patch, MagicMock
import sys
import os
import json

# Добавляем родительскую директорию в sys.path для импорта модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Импортируем функции из clear_data.py
from clear_data import get_token, get_all_zones, delete_zone

class TestClearData:
    """Тесты для функций модуля clear_data.py"""
    
    def test_get_token_success(self, mocker):
        """Тест успешного получения токена"""
        # Создаем мок для requests.post
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "test_token", "token_type": "bearer"}
        
        mocker.patch('requests.post', return_value=mock_response)
        
        # Вызываем тестируемую функцию
        token = get_token()
        
        # Проверяем результат
        assert token == "test_token"
    
    def test_get_token_failure(self, mocker):
        """Тест неудачного получения токена"""
        # Создаем мок для requests.post
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        
        mocker.patch('requests.post', return_value=mock_response)
        
        # Проверяем, что функция вызывает exit(1)
        with pytest.raises(SystemExit) as e:
            get_token()
        
        assert e.value.code == 1
    
    def test_get_all_zones_success(self, mocker):
        """Тест успешного получения списка зон"""
        # Создаем мок для requests.get
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"name": "zone1", "type": "zone", "environments": []},
            {"name": "zone2", "type": "zone", "environments": []}
        ]
        
        mocker.patch('requests.get', return_value=mock_response)
        
        # Вызываем тестируемую функцию
        zones = get_all_zones("test_token")
        
        # Проверяем результат
        assert len(zones) == 2
        assert zones[0]["name"] == "zone1"
        assert zones[1]["name"] == "zone2"
    
    def test_get_all_zones_failure(self, mocker):
        """Тест неудачного получения списка зон"""
        # Создаем мок для requests.get
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        
        mocker.patch('requests.get', return_value=mock_response)
        
        # Вызываем тестируемую функцию
        zones = get_all_zones("test_token")
        
        # Проверяем результат
        assert zones == []
    
    def test_delete_zone_success(self, mocker):
        """Тест успешного удаления зоны"""
        # Создаем мок для requests.delete
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "Zone deleted"}
        
        mocker.patch('requests.delete', return_value=mock_response)
        
        # Вызываем тестируемую функцию
        result = delete_zone("test_token", "zone1")
        
        # Проверяем результат
        assert result is True
    
    def test_delete_zone_failure(self, mocker):
        """Тест неудачного удаления зоны"""
        # Создаем мок для requests.delete
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Zone not found"
        
        mocker.patch('requests.delete', return_value=mock_response)
        
        # Вызываем тестируемую функцию
        result = delete_zone("test_token", "nonexistent_zone")
        
        # Проверяем результат
        assert result is False 