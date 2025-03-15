#!/bin/bash

# Активируем виртуальное окружение
source venv/bin/activate

# Запускаем скрипт очистки данных
echo "Запуск очистки данных..."
python clear_data.py

# Деактивируем виртуальное окружение
deactivate 