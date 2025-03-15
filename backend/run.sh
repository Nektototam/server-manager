#!/bin/bash

# Функция для остановки уже запущенных процессов
cleanup_processes() {
  echo "Проверка и остановка уже запущенных процессов..."
  
  # Остановка PouchDB-сервера, если он запущен
  POUCHDB_PIDS=$(ps aux | grep "node.*pouchdb-server/server.js" | grep -v grep | awk '{print $2}')
  if [ ! -z "$POUCHDB_PIDS" ]; then
    echo "Останавливаем запущенные PouchDB-серверы..."
    for PID in $POUCHDB_PIDS; do
      kill $PID 2>/dev/null
    done
    sleep 1
  fi
  
  # Остановка бэкенда, если он запущен
  BACKEND_PIDS=$(ps aux | grep "uvicorn main:app" | grep -v grep | awk '{print $2}')
  if [ ! -z "$BACKEND_PIDS" ]; then
    echo "Останавливаем запущенные бэкенд-серверы..."
    for PID in $BACKEND_PIDS; do
      kill $PID 2>/dev/null
    done
    sleep 1
  fi
}

# Очистка процессов перед запуском
cleanup_processes

# Активируем виртуальное окружение
source venv/bin/activate

# Устанавливаем зависимости
pip install -r requirements.txt

# Создаем директорию для данных PouchDB, если она не существует
mkdir -p data

# Запускаем PouchDB-сервер в фоновом режиме
echo "Запуск PouchDB-сервера..."
cd pouchdb-server
npm install
DB_PATH="../data" node server.js &
POUCHDB_PID=$!
cd ..

# Ждем запуска PouchDB-сервера
echo "Ожидание запуска PouchDB-сервера..."
sleep 3

# Запускаем API сервер
echo "Запуск API сервера..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# При завершении скрипта останавливаем PouchDB-сервер
trap "kill $POUCHDB_PID 2>/dev/null; deactivate" EXIT 