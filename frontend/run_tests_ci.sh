#!/bin/bash

# Устанавливаем переменную окружения для запуска тестов в CI режиме
export CI=true

# Запускаем тесты
npm test -- --coverage

# Выводим информацию о покрытии
echo "Отчет о покрытии доступен в директории coverage/"
echo "Для просмотра HTML-отчета откройте coverage/lcov-report/index.html в браузере" 