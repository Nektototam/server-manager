#!/bin/bash

# Скрипт для запуска клиента для пакетной работы с данными

# Проверка наличия виртуального окружения
if [ ! -d "venv" ]; then
    echo "Виртуальное окружение не найдено. Создаем..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Проверка наличия файла .env
if [ ! -f ".env" ]; then
    echo "Файл .env не найден. Создаем файл с настройками по умолчанию..."
    cat > .env << EOL
API_URL=http://localhost:8000
API_USERNAME=admin
API_PASSWORD=admin
EOL
    echo "Файл .env создан. При необходимости отредактируйте его."
fi

# Запуск примера использования клиента
echo "Запуск клиента для пакетной работы с данными..."
python batch_client_example.py

# Деактивация виртуального окружения
deactivate

echo "Готово!" 