#!/bin/bash

# Устанавливаем зависимости, если они еще не установлены
if [ ! -d "node_modules" ]; then
  echo "Устанавливаем зависимости..."
  npm install
fi

# Запускаем тесты с покрытием
echo "Запускаем тесты..."
npm test -- --coverage

# Выводим информацию о покрытии
echo "Отчет о покрытии кода доступен в директории coverage/"
echo "Для просмотра HTML-отчета откройте coverage/lcov-report/index.html в браузере" 