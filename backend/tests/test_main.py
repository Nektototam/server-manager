import pytest
from unittest.mock import patch, MagicMock
import sys
import os
import json
from datetime import timedelta

# Добавляем родительскую директорию в sys.path для импорта модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Мокаем create_db_if_not_exists перед импортом main
with patch('requests.put') as mock_put:
    mock_put.return_value.status_code = 201
    # Импортируем функции и классы из main.py
    from main import (
        create_db_if_not_exists, get_doc, save_doc, delete_doc, 
        get_all_docs, verify_password, get_password_hash, 
        get_user, authenticate_user, create_access_token
    )

class TestDatabaseFunctions:
    """Тесты для функций работы с базой данных"""
    
    def test_create_db_if_not_exists_success(self, mocker):
        """Тест успешного создания базы данных"""
        # Создаем мок для requests.put
        mock_response = MagicMock()
        mock_response.status_code = 201
        
        mocker.patch('requests.put', return_value=mock_response)
        
        # Вызываем тестируемую функцию
        result = create_db_if_not_exists("test_db")
        
        # Проверяем результат
        assert result is True
    
    def test_create_db_if_not_exists_already_exists(self, mocker):
        """Тест создания базы данных, которая уже существует"""
        # Создаем мок для requests.put
        mock_response = MagicMock()
        mock_response.status_code = 412
        
        mocker.patch('requests.put', return_value=mock_response)
        
        # Вызываем тестируемую функцию
        result = create_db_if_not_exists("test_db")
        
        # Проверяем результат
        assert result is True
    
    def test_create_db_if_not_exists_failure(self, mocker):
        """Тест неудачного создания базы данных"""
        # Создаем мок для requests.put
        mock_response = MagicMock()
        mock_response.status_code = 500
        
        mocker.patch('requests.put', return_value=mock_response)
        
        # Вызываем тестируемую функцию
        result = create_db_if_not_exists("test_db")
        
        # Проверяем результат
        assert result is False
    
    def test_get_doc_success(self, mocker):
        """Тест успешного получения документа"""
        # Создаем мок для requests.get
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"_id": "test_id", "name": "test_doc"}
        
        mocker.patch('requests.get', return_value=mock_response)
        
        # Вызываем тестируемую функцию
        doc = get_doc("test_db", "test_id")
        
        # Проверяем результат
        assert doc["_id"] == "test_id"
        assert doc["name"] == "test_doc"
    
    def test_get_doc_not_found(self, mocker):
        """Тест получения несуществующего документа"""
        # Создаем мок для requests.get
        mock_response = MagicMock()
        mock_response.status_code = 404
        
        mocker.patch('requests.get', return_value=mock_response)
        
        # Вызываем тестируемую функцию
        doc = get_doc("test_db", "nonexistent_id")
        
        # Проверяем результат
        assert doc is None
    
    def test_save_doc_update_existing(self, mocker):
        """Тест обновления существующего документа"""
        # Создаем моки
        get_doc_mock = MagicMock(return_value={"_id": "test_id", "_rev": "1-abc", "name": "old_name"})
        put_mock = MagicMock()
        put_mock.return_value.status_code = 201
        
        mocker.patch('main.get_doc', get_doc_mock)
        mocker.patch('requests.put', put_mock)
        
        # Вызываем тестируемую функцию
        doc = {"_id": "test_id", "name": "new_name"}
        save_doc("test_db", doc)
        
        # Проверяем, что документ был обновлен с правильным _rev
        assert doc["_rev"] == "1-abc"
        put_mock.assert_called_once()
    
    def test_save_doc_create_new(self, mocker):
        """Тест создания нового документа"""
        # Создаем моки
        get_doc_mock = MagicMock(return_value=None)
        put_mock = MagicMock()
        put_mock.return_value.status_code = 201
        
        mocker.patch('main.get_doc', get_doc_mock)
        mocker.patch('requests.put', put_mock)
        
        # Вызываем тестируемую функцию
        doc = {"_id": "new_id", "name": "new_doc"}
        save_doc("test_db", doc)
        
        # Проверяем, что документ был создан
        assert "_rev" not in doc
        put_mock.assert_called_once()

class TestAuthFunctions:
    """Тесты для функций аутентификации"""
    
    def test_verify_password(self, mocker):
        """Тест проверки пароля"""
        # Создаем мок для CryptContext.verify
        verify_mock = mocker.patch('passlib.context.CryptContext.verify')
        verify_mock.return_value = True
        
        # Вызываем тестируемую функцию
        result = verify_password("password", "hashed_password")
        
        # Проверяем результат
        assert result is True
        verify_mock.assert_called_once_with("password", "hashed_password")
    
    def test_get_password_hash(self, mocker):
        """Тест получения хеша пароля"""
        # Создаем мок для CryptContext.hash
        hash_mock = mocker.patch('passlib.context.CryptContext.hash')
        hash_mock.return_value = "hashed_password"
        
        # Вызываем тестируемую функцию
        result = get_password_hash("password")
        
        # Проверяем результат
        assert result == "hashed_password"
        hash_mock.assert_called_once_with("password")
    
    def test_get_user_exists(self, mocker):
        """Тест получения существующего пользователя"""
        # Создаем мок для get_doc
        get_doc_mock = mocker.patch('main.get_doc')
        get_doc_mock.return_value = {
            "_id": "user:admin",
            "username": "admin",
            "email": "admin@example.com",
            "hashed_password": "hashed_password"
        }
        
        # Вызываем тестируемую функцию
        user = get_user("admin")
        
        # Проверяем результат
        assert user.username == "admin"
        assert user.email == "admin@example.com"
        assert user.hashed_password == "hashed_password"
    
    def test_get_user_not_exists(self, mocker):
        """Тест получения несуществующего пользователя"""
        # Создаем мок для get_doc
        get_doc_mock = mocker.patch('main.get_doc')
        get_doc_mock.return_value = None
        
        # Вызываем тестируемую функцию
        user = get_user("nonexistent")
        
        # Проверяем результат
        assert user is None
    
    def test_authenticate_user_success(self, mocker):
        """Тест успешной аутентификации пользователя"""
        # Создаем моки
        get_user_mock = mocker.patch('main.get_user')
        get_user_mock.return_value = MagicMock(username="admin", hashed_password="hashed_password")
        
        verify_password_mock = mocker.patch('main.verify_password')
        verify_password_mock.return_value = True
        
        # Вызываем тестируемую функцию
        user = authenticate_user("admin", "password")
        
        # Проверяем результат
        assert user is not None
        assert user.username == "admin"
    
    def test_authenticate_user_wrong_password(self, mocker):
        """Тест аутентификации с неправильным паролем"""
        # Создаем моки
        get_user_mock = mocker.patch('main.get_user')
        get_user_mock.return_value = MagicMock(username="admin", hashed_password="hashed_password")
        
        verify_password_mock = mocker.patch('main.verify_password')
        verify_password_mock.return_value = False
        
        # Вызываем тестируемую функцию
        user = authenticate_user("admin", "wrong_password")
        
        # Проверяем результат
        assert user is False
    
    def test_authenticate_user_not_exists(self, mocker):
        """Тест аутентификации несуществующего пользователя"""
        # Создаем мок для get_user
        get_user_mock = mocker.patch('main.get_user')
        get_user_mock.return_value = None
        
        # Вызываем тестируемую функцию
        user = authenticate_user("nonexistent", "password")
        
        # Проверяем результат
        assert user is False
    
    def test_create_access_token(self, mocker):
        """Тест создания токена доступа"""
        # Создаем мок для jwt.encode
        jwt_encode_mock = mocker.patch('jose.jwt.encode')
        jwt_encode_mock.return_value = "test_token"
        
        # Вызываем тестируемую функцию
        data = {"sub": "admin"}
        expires_delta = timedelta(minutes=30)
        token = create_access_token(data, expires_delta)
        
        # Проверяем результат
        assert token == "test_token"
        jwt_encode_mock.assert_called_once() 