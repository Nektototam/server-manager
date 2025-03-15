#!/bin/bash

# Активируем виртуальное окружение
source venv/bin/activate

# Запускаем скрипт проверки данных
echo "Запуск проверки данных..."
python check_data.py

# Деактивируем виртуальное окружение
deactivate 