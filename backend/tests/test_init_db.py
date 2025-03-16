import pytest
from unittest.mock import patch, MagicMock
import sys
import os
import json

# Добавляем родительскую директорию в sys.path для импорта модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Мокаем requests.put перед импортом init_db
with patch('requests.put') as mock_put:
    mock_put.return_value.status_code = 201
    # Импортируем функции из init_db.py
    from init_db import create_db_if_not_exists, create_admin_user, create_initial_data

class TestInitDb:
    """Тесты для функций модуля init_db.py"""
    
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
    
    def test_create_admin_user_new(self, mocker):
        """Тест создания нового пользователя admin"""
        # Мокаем get_doc для возврата None (пользователь не существует)
        get_doc_mock = mocker.patch('init_db.get_doc', return_value=None)
        
        # Мокаем get_password_hash
        get_password_hash_mock = mocker.patch('init_db.get_password_hash', return_value="hashed_password")
        
        # Мокаем save_doc
        save_doc_mock = mocker.patch('init_db.save_doc')
        
        # Вызываем тестируемую функцию
        create_admin_user()
        
        # Проверяем, что функции были вызваны с правильными аргументами
        get_doc_mock.assert_called_once_with("server_resources", "user:admin")
        get_password_hash_mock.assert_called_once_with("admin")
        save_doc_mock.assert_called_once()
        
        # Проверяем, что save_doc была вызвана с правильным документом
        doc = save_doc_mock.call_args[0][1]
        assert doc["_id"] == "user:admin"
        assert doc["username"] == "admin"
        assert doc["email"] == "admin@example.com"
        assert doc["hashed_password"] == "hashed_password"
    
    def test_create_admin_user_exists(self, mocker):
        """Тест создания пользователя admin, который уже существует"""
        # Мокаем get_doc для возврата существующего пользователя
        existing_user = {
            "_id": "user:admin",
            "username": "admin",
            "email": "admin@example.com",
            "hashed_password": "existing_hash"
        }
        get_doc_mock = mocker.patch('init_db.get_doc', return_value=existing_user)
        
        # Мокаем get_password_hash (не должна вызываться)
        get_password_hash_mock = mocker.patch('init_db.get_password_hash')
        
        # Мокаем save_doc (не должна вызываться)
        save_doc_mock = mocker.patch('init_db.save_doc')
        
        # Вызываем тестируемую функцию
        create_admin_user()
        
        # Проверяем, что get_doc была вызвана, а остальные функции - нет
        get_doc_mock.assert_called_once_with("server_resources", "user:admin")
        get_password_hash_mock.assert_not_called()
        save_doc_mock.assert_not_called()
    
    def test_create_initial_data(self, mocker):
        """Тест создания начальных данных"""
        # Мокаем get_all_docs для возврата пустого списка
        get_all_docs_mock = mocker.patch('init_db.get_all_docs', return_value={"rows": []})
        
        # Мокаем save_doc
        save_doc_mock = mocker.patch('init_db.save_doc')
        
        # Вызываем тестируемую функцию
        create_initial_data()
        
        # Проверяем, что функции были вызваны
        get_all_docs_mock.assert_called_once_with("server_resources", include_docs=True)
        
        # Проверяем, что save_doc была вызвана для каждой зоны
        assert save_doc_mock.call_count >= 3  # Минимум 3 зоны должны быть созданы 