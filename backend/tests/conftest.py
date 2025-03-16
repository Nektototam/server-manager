import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# Добавляем родительскую директорию в sys.path для импорта модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Мокаем requests.put для предотвращения реальных запросов к базе данных
@pytest.fixture(autouse=True)
def mock_requests(monkeypatch):
    """Фикстура для мока всех HTTP-запросов"""
    # Создаем мок-объект для ответа
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {}
    
    # Мокаем все методы requests
    with patch('requests.put', return_value=mock_response), \
         patch('requests.get', return_value=mock_response), \
         patch('requests.post', return_value=mock_response), \
         patch('requests.delete', return_value=mock_response):
        yield

@pytest.fixture
def mock_response():
    """Фикстура для создания мока ответа requests"""
    response = MagicMock()
    response.status_code = 200
    return response

@pytest.fixture
def mock_token():
    """Фикстура для создания тестового токена"""
    return "test_token"

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Фикстура для мока переменных окружения"""
    monkeypatch.setenv("POUCHDB_URL", "http://localhost:5984")
    monkeypatch.setenv("SECRET_KEY", "test_secret_key")
    monkeypatch.setenv("ALGORITHM", "HS256")
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30") 