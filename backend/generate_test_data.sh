#!/bin/bash

# Активируем виртуальное окружение
source venv/bin/activate

# Запускаем скрипт генерации тестовых данных
echo "Запуск генерации тестовых данных..."
python generate_test_data.py

# Деактивируем виртуальное окружение
deactivate 