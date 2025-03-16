#!/bin/bash

# Скрипт для запуска тестов клиента

# Проверка наличия виртуального окружения
if [ ! -d "venv" ]; then
    echo "Виртуальное окружение не найдено. Создаем..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Запуск тестов с покрытием
echo "Запуск тестов с покрытием..."
pytest tests/ -v --cov=. --cov-report=term --cov-report=html

# Вывод информации о покрытии
echo "Отчет о покрытии доступен в директории htmlcov/"
echo "Для просмотра HTML-отчета откройте htmlcov/index.html в браузере"

# Деактивация виртуального окружения
deactivate

echo "Готово!" 