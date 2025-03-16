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
    from init_db import create_db_if_not_exists, create_test_users, create_test_zones

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
    
    def test_create_test_users(self, mocker):
        """Тест создания тестовых пользователей"""
        # Мокаем get_doc для возврата None (пользователь не существует)
        get_doc_mock = mocker.patch('init_db.get_doc', return_value=None)
        
        # Мокаем pwd_context.hash
        hash_mock = mocker.patch('init_db.pwd_context.hash', return_value="hashed_password")
        
        # Мокаем save_doc
        save_doc_mock = mocker.patch('init_db.save_doc')
        
        # Вызываем тестируемую функцию
        create_test_users()
        
        # Проверяем, что функции были вызваны
        assert get_doc_mock.call_count >= 1
        assert hash_mock.call_count >= 1
        assert save_doc_mock.call_count >= 1
    
    def test_create_test_zones(self, mocker):
        """Тест создания тестовых зон"""
        # Мокаем get_doc для возврата None (зона не существует)
        get_doc_mock = mocker.patch('init_db.get_doc', return_value=None)
        
        # Мокаем save_doc
        save_doc_mock = mocker.patch('init_db.save_doc')
        
        # Вызываем тестируемую функцию
        create_test_zones()
        
        # Проверяем, что функции были вызваны
        assert get_doc_mock.call_count >= 1
        assert save_doc_mock.call_count >= 1 