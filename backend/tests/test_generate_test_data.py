import pytest
from unittest.mock import patch, MagicMock, call
import sys
import os
import json
import random

# Добавляем родительскую директорию в sys.path для импорта модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Мокаем random.choice и random.randint перед импортом generate_test_data
with patch('random.choice') as mock_choice, \
     patch('random.randint') as mock_randint, \
     patch('requests.put') as mock_put:
    
    mock_choice.return_value = "mocked_choice"
    mock_randint.return_value = 1
    mock_put.return_value.status_code = 201
    
    # Импортируем функции из generate_test_data.py
    from generate_test_data import (
        get_token, get_all_zones, zone_exists, create_zone, 
        get_zone, create_environment, create_server, 
        generate_random_ip, generate_server_data, main
    )

class TestGenerateTestData:
    """Тесты для функций модуля generate_test_data.py"""
    
    def test_get_token(self, mocker):
        """Тест получения токена"""
        # Создаем мок для requests.post
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "test_token", "token_type": "bearer"}
        
        mocker.patch('requests.post', return_value=mock_response)
        
        # Вызываем тестируемую функцию
        token = get_token()
        
        # Проверяем результат
        assert token == "test_token"
    
    def test_get_all_zones(self, mocker):
        """Тест получения всех зон"""
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
    
    def test_zone_exists(self, mocker):
        """Тест проверки существования зоны"""
        # Мокаем get_all_zones
        mocker.patch('generate_test_data.get_all_zones', return_value=[
            {"name": "zone1", "type": "zone", "environments": []},
            {"name": "zone2", "type": "zone", "environments": []}
        ])
        
        # Вызываем тестируемую функцию
        exists_true = zone_exists("test_token", "zone1")
        exists_false = zone_exists("test_token", "nonexistent")
        
        # Проверяем результат
        assert exists_true is True
        assert exists_false is False
    
    def test_create_zone(self, mocker):
        """Тест создания зоны"""
        # Создаем мок для requests.post
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "Zone created"}
        
        mocker.patch('requests.post', return_value=mock_response)
        
        # Вызываем тестируемую функцию
        result = create_zone("test_token", "new_zone")
        
        # Проверяем результат
        assert result is True
    
    def test_get_zone(self, mocker):
        """Тест получения информации о зоне"""
        # Создаем мок для requests.get
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"name": "zone1", "type": "zone", "environments": []}
        
        mocker.patch('requests.get', return_value=mock_response)
        
        # Вызываем тестируемую функцию
        zone = get_zone("test_token", "zone1")
        
        # Проверяем результат
        assert zone["name"] == "zone1"
    
    def test_create_environment(self, mocker):
        """Тест создания окружения"""
        # Создаем мок для requests.post
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "Environment created"}
        
        mocker.patch('requests.post', return_value=mock_response)
        
        # Вызываем тестируемую функцию
        result = create_environment("test_token", "zone1", "prod")
        
        # Проверяем результат
        assert result is True
    
    def test_create_server(self, mocker):
        """Тест создания сервера"""
        # Создаем мок для requests.post
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "Server created"}
        
        mocker.patch('requests.post', return_value=mock_response)
        
        # Вызываем тестируемую функцию
        server_data = {
            "fqdn": "web01.example.com",
            "ip": "192.168.1.1",
            "server_type": "web",
            "status": "available"
        }
        result = create_server("test_token", "zone1", "prod", server_data)
        
        # Проверяем результат
        assert result is True
    
    def test_generate_random_ip(self, mocker):
        """Тест генерации случайного IP-адреса"""
        # Мокаем random.randint для предсказуемых результатов
        mocker.patch('random.randint', side_effect=[192, 168, 1, 10])
        
        # Вызываем тестируемую функцию
        ip = generate_random_ip()
        
        # Проверяем результат
        assert ip == "192.168.1.10"
    
    def test_generate_server_data(self, mocker):
        """Тест генерации данных сервера"""
        # Мокаем random.choice
        mocker.patch('random.choice', return_value="available")
        
        # Мокаем generate_random_ip
        mocker.patch('generate_test_data.generate_random_ip', return_value="192.168.1.10")
        
        # Вызываем тестируемую функцию
        server_data = generate_server_data("zone1", "prod", 1)
        
        # Проверяем результат
        assert "fqdn" in server_data
        assert server_data["ip"] == "192.168.1.10"
        assert "server_type" in server_data
        assert server_data["status"] == "available"
    
    def test_main(self, mocker):
        """Тест основной функции"""
        # Мокаем get_token
        mocker.patch('generate_test_data.get_token', return_value="test_token")
        
        # Мокаем get_all_zones
        mocker.patch('generate_test_data.get_all_zones', return_value=[])
        
        # Мокаем zone_exists
        mocker.patch('generate_test_data.zone_exists', return_value=False)
        
        # Мокаем create_zone
        create_zone_mock = mocker.patch('generate_test_data.create_zone', return_value=True)
        
        # Мокаем create_environment
        create_env_mock = mocker.patch('generate_test_data.create_environment', return_value=True)
        
        # Мокаем create_server
        create_server_mock = mocker.patch('generate_test_data.create_server', return_value=True)
        
        # Мокаем generate_server_data
        mocker.patch('generate_test_data.generate_server_data', return_value={
            "fqdn": "web01.example.com",
            "ip": "192.168.1.1",
            "server_type": "web",
            "status": "available"
        })
        
        # Мокаем time.sleep чтобы тест не ждал
        mocker.patch('time.sleep')
        
        # Вызываем тестируемую функцию с минимальными параметрами для быстрого выполнения
        # Перехватываем sys.exit
        with patch('sys.exit'):
            main()
        
        # Проверяем, что основные функции были вызваны
        assert create_zone_mock.call_count >= 1
        assert create_env_mock.call_count >= 1
        assert create_server_mock.call_count >= 1 