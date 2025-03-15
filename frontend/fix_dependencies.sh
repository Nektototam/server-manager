#!/bin/bash

echo "Очистка node_modules..."
rm -rf node_modules
rm -f package-lock.json

echo "Установка зависимостей..."
npm install

echo "Зависимости успешно переустановлены!" 