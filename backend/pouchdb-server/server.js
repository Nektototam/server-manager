const express = require('express');
const PouchDB = require('pouchdb');
const ExpressPouchDB = require('express-pouchdb');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 5984;
const DB_PATH = process.env.DB_PATH || './data';

// Настройка CORS
app.use(cors({
  origin: '*',
  credentials: true,
  methods: ['GET', 'PUT', 'POST', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With', 'Origin']
}));

// Настройка PouchDB
const PouchDBServer = ExpressPouchDB(PouchDB.defaults({
  prefix: DB_PATH + '/'
}));

// Использование Express PouchDB
app.use('/', PouchDBServer);

// Функция для запуска сервера с обработкой ошибок
const startServer = (port) => {
  const server = app.listen(port, () => {
    console.log(`PouchDB Server запущен на порту ${port}`);
    console.log(`Данные хранятся в директории: ${DB_PATH}`);
  }).on('error', (err) => {
    if (err.code === 'EADDRINUSE') {
      console.log(`Порт ${port} уже используется, пробуем порт ${port + 1}`);
      startServer(port + 1);
    } else {
      console.error('Ошибка запуска сервера:', err);
      process.exit(1);
    }
  });
};

// Запуск сервера
startServer(PORT); 