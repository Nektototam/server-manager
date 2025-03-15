#!/bin/bash

# Активация виртуального окружения
echo "Активация виртуального окружения..."
source venv/bin/activate

# Вывод информации о Python и pip
echo "Информация о Python:"
python --version
echo "Информация о pip:"
pip --version

echo "Виртуальное окружение активировано. Для деактивации введите 'deactivate'." 