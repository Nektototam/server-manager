#!/bin/bash

# Активация виртуального окружения
source venv/bin/activate

# Установка зависимостей для тестирования
pip install pytest pytest-mock pytest-cov httpx==0.23.0

# Запуск тестов с покрытием
echo "Запуск тестов с отчетом о покрытии..."
python -m pytest tests/test_check_data.py tests/test_clear_data.py tests/test_main.py tests/test_init_db.py tests/test_generate_test_data.py -v --cov=. --cov-report=term --cov-report=html

# Вывод информации о покрытии
echo "Отчет о покрытии кода тестами сохранен в директории htmlcov/"
echo "Для просмотра отчета откройте файл htmlcov/index.html в браузере"

# Деактивация виртуального окружения
deactivate 