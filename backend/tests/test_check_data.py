import pytest
from unittest.mock import patch, MagicMock
import sys
import os
import json

# Добавляем родительскую директорию в sys.path для импорта модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Импортируем функции из check_data.py
from check_data import get_token, get_all_zones, get_zone

class TestCheckData:
    """Тесты для функций модуля check_data.py"""
    
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
    
    def test_get_zone_success(self, mocker):
        """Тест успешного получения информации о зоне"""
        # Создаем мок для requests.get
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "name": "zone1", 
            "type": "zone", 
            "environments": [
                {"name": "prod", "servers": []}
            ]
        }
        
        mocker.patch('requests.get', return_value=mock_response)
        
        # Вызываем тестируемую функцию
        zone = get_zone("test_token", "zone1")
        
        # Проверяем результат
        assert zone["name"] == "zone1"
        assert len(zone["environments"]) == 1
        assert zone["environments"][0]["name"] == "prod"
    
    def test_get_zone_failure(self, mocker):
        """Тест неудачного получения информации о зоне"""
        # Создаем мок для requests.get
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        
        mocker.patch('requests.get', return_value=mock_response)
        
        # Вызываем тестируемую функцию
        zone = get_zone("test_token", "nonexistent_zone")
        
        # Проверяем результат
        assert zone is None 