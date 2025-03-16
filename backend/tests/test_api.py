import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os
import json

# Добавляем родительскую директорию в sys.path для импорта модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Импортируем приложение FastAPI из main.py
from main import app, get_user, authenticate_user, create_access_token

# Создаем тестовый клиент
client = TestClient(app)

# Фикстура для мока аутентификации
@pytest.fixture
def mock_auth(mocker):
    # Мок для get_user
    user_mock = MagicMock()
    user_mock.username = "testuser"
    user_mock.email = "test@example.com"
    user_mock.full_name = "Test User"
    user_mock.disabled = False
    user_mock.hashed_password = "hashed_password"
    
    mocker.patch('main.get_user', return_value=user_mock)
    
    # Мок для verify_password
    mocker.patch('main.verify_password', return_value=True)
    
    # Мок для create_access_token
    mocker.patch('main.create_access_token', return_value="test_token")
    
    return user_mock

class TestAuth:
    """Тесты для аутентификации"""
    
    def test_login_success(self, mock_auth):
        """Тест успешного входа в систему"""
        response = client.post(
            "/token",
            data={"username": "testuser", "password": "password"}
        )
        
        assert response.status_code == 200
        assert response.json() == {"access_token": "test_token", "token_type": "bearer"}
    
    def test_login_invalid_credentials(self, mocker):
        """Тест входа с неверными учетными данными"""
        # Мок для authenticate_user
        mocker.patch('main.authenticate_user', return_value=False)
        
        response = client.post(
            "/token",
            data={"username": "testuser", "password": "wrong_password"}
        )
        
        assert response.status_code == 401
        assert "detail" in response.json()
    
    def test_get_current_user(self, mock_auth):
        """Тест получения текущего пользователя"""
        response = client.get(
            "/users/me",
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 200
        assert response.json()["username"] == "testuser"
        assert response.json()["email"] == "test@example.com"

class TestZones:
    """Тесты для API зон"""
    
    @pytest.fixture
    def mock_zones_db(self, mocker, mock_auth):
        """Фикстура для мока базы данных зон"""
        # Мок для get_all_docs
        zones_data = [
            {"_id": "zone:zone1", "name": "zone1", "type": "zone", "environments": []},
            {"_id": "zone:zone2", "name": "zone2", "type": "zone", "environments": []}
        ]
        mocker.patch('main.get_all_docs', return_value=zones_data)
        
        # Мок для get_doc
        def mock_get_doc(db_name, doc_id):
            if doc_id == "zone:zone1":
                return {"_id": "zone:zone1", "name": "zone1", "type": "zone", "environments": []}
            return None
        
        mocker.patch('main.get_doc', side_effect=mock_get_doc)
        
        # Мок для save_doc
        save_doc_mock = mocker.patch('main.save_doc')
        
        # Мок для delete_doc
        delete_doc_mock = mocker.patch('main.delete_doc')
        
        return {
            "zones_data": zones_data,
            "save_doc_mock": save_doc_mock,
            "delete_doc_mock": delete_doc_mock
        }
    
    def test_get_all_zones(self, mock_zones_db):
        """Тест получения всех зон"""
        response = client.get(
            "/zones/",
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 200
        assert len(response.json()) == 2
        assert response.json()[0]["name"] == "zone1"
        assert response.json()[1]["name"] == "zone2"
    
    def test_get_zone(self, mock_zones_db):
        """Тест получения конкретной зоны"""
        response = client.get(
            "/zones/zone1",
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 200
        assert response.json()["name"] == "zone1"
    
    def test_get_zone_not_found(self, mock_zones_db):
        """Тест получения несуществующей зоны"""
        response = client.get(
            "/zones/nonexistent",
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 404
    
    def test_create_zone(self, mock_zones_db):
        """Тест создания новой зоны"""
        response = client.post(
            "/zones/",
            headers={"Authorization": "Bearer test_token"},
            json={"name": "new_zone", "type": "zone", "environments": []}
        )
        
        assert response.status_code == 200
        assert "message" in response.json()
        mock_zones_db["save_doc_mock"].assert_called_once()
    
    def test_update_zone(self, mock_zones_db):
        """Тест обновления зоны"""
        response = client.put(
            "/zones/zone1",
            headers={"Authorization": "Bearer test_token"},
            json={"name": "zone1", "type": "zone", "environments": [{"name": "prod", "servers": []}]}
        )
        
        assert response.status_code == 200
        assert "message" in response.json()
        mock_zones_db["save_doc_mock"].assert_called_once()
    
    def test_delete_zone(self, mock_zones_db):
        """Тест удаления зоны"""
        response = client.delete(
            "/zones/zone1",
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 200
        assert "message" in response.json()
        mock_zones_db["delete_doc_mock"].assert_called_once()

class TestEnvironments:
    """Тесты для API окружений"""
    
    @pytest.fixture
    def mock_env_db(self, mocker, mock_auth):
        """Фикстура для мока базы данных окружений"""
        # Мок для get_doc
        def mock_get_doc(db_name, doc_id):
            if doc_id == "zone:zone1":
                return {
                    "_id": "zone:zone1", 
                    "name": "zone1", 
                    "type": "zone", 
                    "environments": [
                        {"name": "prod", "servers": []}
                    ]
                }
            return None
        
        mocker.patch('main.get_doc', side_effect=mock_get_doc)
        
        # Мок для save_doc
        save_doc_mock = mocker.patch('main.save_doc')
        
        return {
            "save_doc_mock": save_doc_mock
        }
    
    def test_create_environment(self, mock_env_db):
        """Тест создания нового окружения"""
        response = client.post(
            "/zones/zone1/environments/",
            headers={"Authorization": "Bearer test_token"},
            json={"name": "dev", "servers": []}
        )
        
        assert response.status_code == 200
        assert "message" in response.json()
        mock_env_db["save_doc_mock"].assert_called_once()
    
    def test_update_environment(self, mock_env_db):
        """Тест обновления окружения"""
        response = client.put(
            "/zones/zone1/environments/prod",
            headers={"Authorization": "Bearer test_token"},
            json={"name": "prod", "servers": [{"fqdn": "server1.example.com", "ip": "192.168.1.1", "status": "available", "server_type": "web"}]}
        )
        
        assert response.status_code == 200
        assert "message" in response.json()
        mock_env_db["save_doc_mock"].assert_called_once()
    
    def test_delete_environment(self, mock_env_db):
        """Тест удаления окружения"""
        response = client.delete(
            "/zones/zone1/environments/prod",
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 200
        assert "message" in response.json()
        mock_env_db["save_doc_mock"].assert_called_once() 