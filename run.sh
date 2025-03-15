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
  
  # Остановка React-приложения, если оно запущено
  REACT_PIDS=$(ps aux | grep "node.*react-scripts/scripts/start.js" | grep -v grep | awk '{print $2}')
  if [ ! -z "$REACT_PIDS" ]; then
    echo "Останавливаем запущенные React-приложения..."
    for PID in $REACT_PIDS; do
      kill $PID 2>/dev/null
    done
    sleep 1
  fi
}

# Очистка процессов перед запуском
cleanup_processes

# Запуск PouchDB-сервера в фоновом режиме
echo "Запуск PouchDB-сервера..."
cd backend
mkdir -p data
cd pouchdb-server
npm install
DB_PATH="../data" node server.js &
POUCHDB_PID=$!
cd ../..

# Ждем запуска PouchDB-сервера
echo "Ожидание запуска PouchDB-сервера..."
sleep 3

# Запуск бэкенда в фоновом режиме
echo "Запуск бэкенда..."
cd backend
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
deactivate
cd ..

# Ждем запуска бэкенда
echo "Ожидание запуска бэкенда..."
sleep 5

# Запуск фронтенда
echo "Запуск фронтенда..."
cd frontend
npm install

# Если установка зависимостей не удалась, запускаем скрипт исправления
if [ $? -ne 0 ]; then
  echo "Возникла проблема с зависимостями. Запускаем скрипт исправления..."
  ./fix_dependencies.sh
fi

npm start

# При завершении скрипта останавливаем бэкенд и PouchDB-сервер
trap "kill $BACKEND_PID $POUCHDB_PID 2>/dev/null" EXIT 