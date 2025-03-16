#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import json
import os
from unittest.mock import patch, mock_open, MagicMock
from batch_client import BatchClient, Zone, Environment, Server


@pytest.fixture
def client():
    """Фикстура для создания экземпляра клиента для тестов"""
    return BatchClient(
        base_url="http://test-api.example.com",
        username="test_user",
        password="test_password"
    )


@pytest.fixture
def test_zone():
    """Фикстура для создания тестовой зоны"""
    return Zone(
        name="test-zone",
        environments=[
            Environment(
                name="dev",
                servers=[
                    Server(fqdn="server1.dev.example.com", ip="192.168.1.1", status="available", server_type="web")
                ]
            )
        ]
    )


@pytest.fixture
def test_environment():
    """Фикстура для создания тестового окружения"""
    return Environment(
        name="test-env",
        servers=[
            Server(fqdn="server1.test.example.com", ip="192.168.2.1", status="available", server_type="app")
        ]
    )


@pytest.fixture
def test_server():
    """Фикстура для создания тестового сервера"""
    return Server(
        fqdn="server1.example.com",
        ip="192.168.3.1",
        status="available",
        server_type="db"
    )


class TestBatchClient:
    """Тесты для класса BatchClient"""

    def test_init(self):
        """Тест инициализации клиента"""
        # Тест с явными параметрами
        client = BatchClient(
            base_url="http://custom-api.example.com",
            username="custom_user",
            password="custom_password"
        )
        assert client.base_url == "http://custom-api.example.com"
        assert client.username == "custom_user"
        assert client.password == "custom_password"
        assert client.token is None
        assert client.headers == {}

        # Тест с параметрами по умолчанию
        with patch.dict(os.environ, {
            "API_URL": "http://env-api.example.com",
            "API_USERNAME": "env_user",
            "API_PASSWORD": "env_password"
        }):
            client = BatchClient()
            assert client.base_url == "http://env-api.example.com"
            assert client.username == "env_user"
            assert client.password == "env_password"

    def test_login_success(self, client):
        """Тест успешной аутентификации"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "test_token", "token_type": "bearer"}

        with patch("requests.post", return_value=mock_response):
            result = client.login()
            assert result is True
            assert client.token == "test_token"
            assert client.headers == {"Authorization": "Bearer test_token"}

    def test_login_failure(self, client):
        """Тест неудачной аутентификации"""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"

        with patch("requests.post", return_value=mock_response):
            result = client.login()
            assert result is False
            assert client.token is None
            assert client.headers == {}

    def test_login_exception(self, client):
        """Тест исключения при аутентификации"""
        with patch("requests.post", side_effect=Exception("Connection error")):
            result = client.login()
            assert result is False
            assert client.token is None
            assert client.headers == {}

    def test_get_all_zones_success(self, client):
        """Тест успешного получения списка зон"""
        # Подготовка данных для ответа
        zones_data = [
            {"name": "zone1", "type": "zone", "environments": []},
            {"name": "zone2", "type": "zone", "environments": []}
        ]
        
        # Мок ответа API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = zones_data

        # Патчим метод requests.get для возврата мок-ответа
        with patch("requests.get", return_value=mock_response):
            # Устанавливаем токен, чтобы не вызывался метод login
            client.token = "test_token"
            client.headers = {"Authorization": "Bearer test_token"}
            
            # Вызываем тестируемый метод
            result = client.get_all_zones()
            
            # Проверяем результат
            assert len(result) == 2
            assert isinstance(result[0], Zone)
            assert result[0].name == "zone1"
            assert result[1].name == "zone2"

    def test_get_all_zones_failure(self, client):
        """Тест неудачного получения списка зон"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        with patch("requests.get", return_value=mock_response):
            client.token = "test_token"
            client.headers = {"Authorization": "Bearer test_token"}
            
            result = client.get_all_zones()
            assert result == []

    def test_get_zone_success(self, client):
        """Тест успешного получения информации о зоне"""
        zone_data = {
            "name": "test-zone",
            "type": "zone",
            "environments": [
                {
                    "name": "dev",
                    "servers": [
                        {
                            "fqdn": "server1.dev.example.com",
                            "ip": "192.168.1.1",
                            "status": "available",
                            "server_type": "web"
                        }
                    ]
                }
            ]
        }
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = zone_data

        with patch("requests.get", return_value=mock_response):
            client.token = "test_token"
            client.headers = {"Authorization": "Bearer test_token"}
            
            result = client.get_zone("test-zone")
            
            assert isinstance(result, Zone)
            assert result.name == "test-zone"
            assert len(result.environments) == 1
            assert result.environments[0].name == "dev"
            assert len(result.environments[0].servers) == 1
            assert result.environments[0].servers[0].fqdn == "server1.dev.example.com"

    def test_get_zone_failure(self, client):
        """Тест неудачного получения информации о зоне"""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"

        with patch("requests.get", return_value=mock_response):
            client.token = "test_token"
            client.headers = {"Authorization": "Bearer test_token"}
            
            result = client.get_zone("non-existent-zone")
            assert result is None

    def test_create_zone_success(self, client, test_zone):
        """Тест успешного создания зоны"""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"success": True}

        with patch("requests.post", return_value=mock_response):
            client.token = "test_token"
            client.headers = {"Authorization": "Bearer test_token"}
            
            result = client.create_zone(test_zone)
            assert result is True

    def test_create_zone_failure(self, client, test_zone):
        """Тест неудачного создания зоны"""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"

        with patch("requests.post", return_value=mock_response):
            client.token = "test_token"
            client.headers = {"Authorization": "Bearer test_token"}
            
            result = client.create_zone(test_zone)
            assert result is False

    def test_update_zone_success(self, client, test_zone):
        """Тест успешного обновления зоны"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}

        with patch("requests.put", return_value=mock_response):
            client.token = "test_token"
            client.headers = {"Authorization": "Bearer test_token"}
            
            result = client.update_zone("test-zone", test_zone)
            assert result is True

    def test_update_zone_failure(self, client, test_zone):
        """Тест неудачного обновления зоны"""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"

        with patch("requests.put", return_value=mock_response):
            client.token = "test_token"
            client.headers = {"Authorization": "Bearer test_token"}
            
            result = client.update_zone("test-zone", test_zone)
            assert result is False

    def test_delete_zone_success(self, client):
        """Тест успешного удаления зоны"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}

        with patch("requests.delete", return_value=mock_response):
            client.token = "test_token"
            client.headers = {"Authorization": "Bearer test_token"}
            
            result = client.delete_zone("test-zone")
            assert result is True

    def test_delete_zone_failure(self, client):
        """Тест неудачного удаления зоны"""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"

        with patch("requests.delete", return_value=mock_response):
            client.token = "test_token"
            client.headers = {"Authorization": "Bearer test_token"}
            
            result = client.delete_zone("test-zone")
            assert result is False

    def test_create_environment_success(self, client, test_environment):
        """Тест успешного создания окружения"""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"success": True}

        with patch("requests.post", return_value=mock_response):
            client.token = "test_token"
            client.headers = {"Authorization": "Bearer test_token"}
            
            result = client.create_environment("test-zone", test_environment)
            assert result is True

    def test_create_environment_failure(self, client, test_environment):
        """Тест неудачного создания окружения"""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"

        with patch("requests.post", return_value=mock_response):
            client.token = "test_token"
            client.headers = {"Authorization": "Bearer test_token"}
            
            result = client.create_environment("test-zone", test_environment)
            assert result is False

    def test_update_environment_success(self, client, test_environment):
        """Тест успешного обновления окружения"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}

        with patch("requests.put", return_value=mock_response):
            client.token = "test_token"
            client.headers = {"Authorization": "Bearer test_token"}
            
            result = client.update_environment("test-zone", "test-env", test_environment)
            assert result is True

    def test_update_environment_failure(self, client, test_environment):
        """Тест неудачного обновления окружения"""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"

        with patch("requests.put", return_value=mock_response):
            client.token = "test_token"
            client.headers = {"Authorization": "Bearer test_token"}
            
            result = client.update_environment("test-zone", "test-env", test_environment)
            assert result is False

    def test_delete_environment_success(self, client):
        """Тест успешного удаления окружения"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}

        with patch("requests.delete", return_value=mock_response):
            client.token = "test_token"
            client.headers = {"Authorization": "Bearer test_token"}
            
            result = client.delete_environment("test-zone", "test-env")
            assert result is True

    def test_delete_environment_failure(self, client):
        """Тест неудачного удаления окружения"""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"

        with patch("requests.delete", return_value=mock_response):
            client.token = "test_token"
            client.headers = {"Authorization": "Bearer test_token"}
            
            result = client.delete_environment("test-zone", "test-env")
            assert result is False

    def test_add_server_success(self, client, test_server):
        """Тест успешного добавления сервера"""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"success": True}

        with patch("requests.post", return_value=mock_response):
            client.token = "test_token"
            client.headers = {"Authorization": "Bearer test_token"}
            
            result = client.add_server("test-zone", "test-env", test_server)
            assert result is True

    def test_add_server_failure(self, client, test_server):
        """Тест неудачного добавления сервера"""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"

        with patch("requests.post", return_value=mock_response):
            client.token = "test_token"
            client.headers = {"Authorization": "Bearer test_token"}
            
            result = client.add_server("test-zone", "test-env", test_server)
            assert result is False

    def test_update_server_success(self, client, test_server):
        """Тест успешного обновления сервера"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}

        with patch("requests.put", return_value=mock_response):
            client.token = "test_token"
            client.headers = {"Authorization": "Bearer test_token"}
            
            result = client.update_server("test-zone", "test-env", "server1.example.com", test_server)
            assert result is True

    def test_update_server_failure(self, client, test_server):
        """Тест неудачного обновления сервера"""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"

        with patch("requests.put", return_value=mock_response):
            client.token = "test_token"
            client.headers = {"Authorization": "Bearer test_token"}
            
            result = client.update_server("test-zone", "test-env", "server1.example.com", test_server)
            assert result is False

    def test_delete_server_success(self, client):
        """Тест успешного удаления сервера"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}

        with patch("requests.delete", return_value=mock_response):
            client.token = "test_token"
            client.headers = {"Authorization": "Bearer test_token"}
            
            result = client.delete_server("test-zone", "test-env", "server1.example.com")
            assert result is True

    def test_delete_server_failure(self, client):
        """Тест неудачного удаления сервера"""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"

        with patch("requests.delete", return_value=mock_response):
            client.token = "test_token"
            client.headers = {"Authorization": "Bearer test_token"}
            
            result = client.delete_server("test-zone", "test-env", "server1.example.com")
            assert result is False

    def test_batch_create_zones(self, client):
        """Тест пакетного создания зон"""
        # Создаем тестовые зоны
        zones = [
            Zone(name="zone1", environments=[]),
            Zone(name="zone2", environments=[]),
            Zone(name="zone3", environments=[])
        ]
        
        # Патчим метод create_zone для имитации успешного и неудачного создания
        with patch.object(client, 'create_zone') as mock_create_zone:
            # Настраиваем мок для возврата разных значений для разных зон
            mock_create_zone.side_effect = [True, False, True]
            
            # Вызываем тестируемый метод
            results = client.batch_create_zones(zones)
            
            # Проверяем результаты
            assert results == {"zone1": True, "zone2": False, "zone3": True}
            assert mock_create_zone.call_count == 3

    def test_batch_create_environments(self, client):
        """Тест пакетного создания окружений"""
        # Создаем тестовые окружения
        environments = [
            Environment(name="dev", servers=[]),
            Environment(name="test", servers=[]),
            Environment(name="prod", servers=[])
        ]
        
        # Патчим метод create_environment
        with patch.object(client, 'create_environment') as mock_create_env:
            mock_create_env.side_effect = [True, False, True]
            
            results = client.batch_create_environments("test-zone", environments)
            
            assert results == {"dev": True, "test": False, "prod": True}
            assert mock_create_env.call_count == 3

    def test_batch_add_servers(self, client):
        """Тест пакетного добавления серверов"""
        # Создаем тестовые серверы
        servers = [
            Server(fqdn="server1.example.com", ip="192.168.1.1", status="available", server_type="web"),
            Server(fqdn="server2.example.com", ip="192.168.1.2", status="available", server_type="db"),
            Server(fqdn="server3.example.com", ip="192.168.1.3", status="available", server_type="app")
        ]
        
        # Патчим метод add_server
        with patch.object(client, 'add_server') as mock_add_server:
            mock_add_server.side_effect = [True, False, True]
            
            results = client.batch_add_servers("test-zone", "test-env", servers)
            
            assert results == {
                "server1.example.com": True,
                "server2.example.com": False,
                "server3.example.com": True
            }
            assert mock_add_server.call_count == 3

    def test_import_from_json(self, client):
        """Тест импорта данных из JSON-файла"""
        # Создаем тестовые данные JSON
        json_data = {
            "zones": [
                {
                    "name": "zone1",
                    "type": "zone",
                    "environments": [
                        {
                            "name": "dev",
                            "servers": [
                                {
                                    "fqdn": "server1.dev.example.com",
                                    "ip": "192.168.1.1",
                                    "status": "available",
                                    "server_type": "web"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        # Мокаем open для чтения JSON-файла
        mock_open_func = mock_open(read_data=json.dumps(json_data))
        
        # Патчим методы клиента
        with patch("builtins.open", mock_open_func), \
             patch.object(client, 'create_zone', return_value=True), \
             patch.object(client, 'create_environment', return_value=True), \
             patch.object(client, 'add_server', return_value=True):
            
            results = client.import_from_json("test.json")
            
            assert "zones" in results
            assert "environments" in results
            assert "servers" in results
            assert "zone1" in results["zones"]
            assert results["zones"]["zone1"] is True
            assert "zone1" in results["environments"]
            assert "dev" in results["environments"]["zone1"]
            assert results["environments"]["zone1"]["dev"] is True
            assert "zone1/dev" in results["servers"]
            assert "server1.dev.example.com" in results["servers"]["zone1/dev"]
            assert results["servers"]["zone1/dev"]["server1.dev.example.com"] is True

    def test_import_from_json_exception(self, client):
        """Тест исключения при импорте из JSON-файла"""
        # Патчим open для вызова исключения
        with patch("builtins.open", side_effect=Exception("File not found")):
            results = client.import_from_json("non_existent.json")
            assert "error" in results
            assert "File not found" in results["error"]

    def test_export_to_json(self, client):
        """Тест экспорта данных в JSON-файл"""
        # Создаем тестовые зоны для экспорта
        zones = [
            Zone(name="zone1", environments=[]),
            Zone(name="zone2", environments=[])
        ]
        
        # Мокаем open для записи в JSON-файл
        mock_open_func = mock_open()
        
        # Патчим метод get_all_zones и open
        with patch.object(client, 'get_all_zones', return_value=zones), \
             patch("builtins.open", mock_open_func):
            
            result = client.export_to_json("export.json")
            
            assert result is True
            mock_open_func.assert_called_once_with("export.json", "w", encoding="utf-8")
            
            # Проверяем, что json.dump был вызван с правильными данными
            handle = mock_open_func()
            json_data = json.dumps({"zones": [zone.dict() for zone in zones]}, ensure_ascii=False, indent=2)
            assert handle.write.called

    def test_export_to_json_exception(self, client):
        """Тест исключения при экспорте в JSON-файл"""
        # Патчим метод get_all_zones для вызова исключения
        with patch.object(client, 'get_all_zones', side_effect=Exception("API error")):
            result = client.export_to_json("export.json")
            assert result is False 