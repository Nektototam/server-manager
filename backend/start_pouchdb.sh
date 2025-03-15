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
}

# Очистка процессов перед запуском
cleanup_processes

# Создаем директорию для данных, если она не существует
mkdir -p data

# Переходим в директорию pouchdb-server
cd pouchdb-server

# Устанавливаем зависимости, если они еще не установлены
npm install

# Запускаем PouchDB-сервер
echo "Запуск PouchDB-сервера..."
DB_PATH="../data" npm start 