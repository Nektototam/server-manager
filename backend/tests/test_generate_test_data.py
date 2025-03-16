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
        get_token, generate_server_name, generate_ip, generate_server, 
        generate_servers, generate_environment, generate_environments, 
        generate_zone, generate_zones, generate_test_data
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
    
    def test_generate_server_name(self, mocker):
        """Тест генерации имени сервера"""
        # Мокаем random.choice для предсказуемых результатов
        mocker.patch('random.choice', side_effect=["app", "01", "prod"])
        
        # Вызываем тестируемую функцию
        server_name = generate_server_name("web")
        
        # Проверяем результат
        assert server_name == "web-app01.prod.example.com"
    
    def test_generate_ip(self, mocker):
        """Тест генерации IP-адреса"""
        # Мокаем random.randint для предсказуемых результатов
        mocker.patch('random.randint', side_effect=[192, 168, 1, 10])
        
        # Вызываем тестируемую функцию
        ip = generate_ip()
        
        # Проверяем результат
        assert ip == "192.168.1.10"
    
    def test_generate_server(self, mocker):
        """Тест генерации сервера"""
        # Мокаем вспомогательные функции
        mocker.patch('generate_test_data.generate_server_name', return_value="web-app01.prod.example.com")
        mocker.patch('generate_test_data.generate_ip', return_value="192.168.1.10")
        mocker.patch('random.choice', return_value="available")
        
        # Вызываем тестируемую функцию
        server = generate_server("web")
        
        # Проверяем результат
        assert server["fqdn"] == "web-app01.prod.example.com"
        assert server["ip"] == "192.168.1.10"
        assert server["server_type"] == "web"
        assert server["status"] == "available"
    
    def test_generate_servers(self, mocker):
        """Тест генерации списка серверов"""
        # Мокаем generate_server для предсказуемых результатов
        mock_server = {"fqdn": "test-server", "ip": "192.168.1.1", "server_type": "web", "status": "available"}
        mocker.patch('generate_test_data.generate_server', return_value=mock_server)
        
        # Вызываем тестируемую функцию с разными параметрами
        servers_1 = generate_servers(1, "web")
        servers_3 = generate_servers(3, "db")
        
        # Проверяем результаты
        assert len(servers_1) == 1
        assert servers_1[0] == mock_server
        
        assert len(servers_3) == 3
        assert all(server == mock_server for server in servers_3)
    
    def test_generate_environment(self, mocker):
        """Тест генерации окружения"""
        # Мокаем generate_servers
        mock_servers = [{"fqdn": "test-server", "ip": "192.168.1.1", "server_type": "web", "status": "available"}]
        mocker.patch('generate_test_data.generate_servers', return_value=mock_servers)
        
        # Вызываем тестируемую функцию
        env = generate_environment("prod", 1, 1, 1)
        
        # Проверяем результат
        assert env["name"] == "prod"
        assert len(env["servers"]) == 3  # 1 web + 1 app + 1 db = 3 сервера
        assert all(server == mock_servers[0] for server in env["servers"])
    
    def test_generate_environments(self, mocker):
        """Тест генерации списка окружений"""
        # Мокаем generate_environment
        mock_env = {"name": "prod", "servers": [{"fqdn": "test-server"}]}
        mocker.patch('generate_test_data.generate_environment', return_value=mock_env)
        
        # Вызываем тестируемую функцию
        envs = generate_environments()
        
        # Проверяем результат
        assert len(envs) == 3  # По умолчанию 3 окружения: prod, stage, dev
        assert all(env == mock_env for env in envs)
    
    def test_generate_zone(self, mocker):
        """Тест генерации зоны"""
        # Мокаем generate_environments
        mock_envs = [{"name": "prod", "servers": []}]
        mocker.patch('generate_test_data.generate_environments', return_value=mock_envs)
        
        # Вызываем тестируемую функцию
        zone = generate_zone("zone1")
        
        # Проверяем результат
        assert zone["_id"] == "zone:zone1"
        assert zone["name"] == "zone1"
        assert zone["type"] == "zone"
        assert zone["environments"] == mock_envs
    
    def test_generate_zones(self, mocker):
        """Тест генерации списка зон"""
        # Мокаем generate_zone
        mock_zone = {"_id": "zone:test", "name": "test", "type": "zone", "environments": []}
        mocker.patch('generate_test_data.generate_zone', return_value=mock_zone)
        
        # Вызываем тестируемую функцию
        zones = generate_zones(["zone1", "zone2"])
        
        # Проверяем результат
        assert len(zones) == 2
        assert all(zone == mock_zone for zone in zones)
    
    def test_generate_test_data(self, mocker):
        """Тест генерации тестовых данных"""
        # Мокаем get_token
        mocker.patch('generate_test_data.get_token', return_value="test_token")
        
        # Мокаем get_all_docs для возврата пустого списка
        mocker.patch('generate_test_data.get_all_docs', return_value={"rows": []})
        
        # Мокаем generate_zones
        mock_zones = [
            {"_id": "zone:zone1", "name": "zone1", "type": "zone", "environments": []},
            {"_id": "zone:zone2", "name": "zone2", "type": "zone", "environments": []}
        ]
        mocker.patch('generate_test_data.generate_zones', return_value=mock_zones)
        
        # Мокаем save_doc
        save_doc_mock = mocker.patch('generate_test_data.save_doc')
        
        # Вызываем тестируемую функцию
        generate_test_data()
        
        # Проверяем, что save_doc была вызвана для каждой зоны
        assert save_doc_mock.call_count == 2
        save_doc_mock.assert_has_calls([
            call("server_resources", mock_zones[0]),
            call("server_resources", mock_zones[1])
        ]) 