# Фронтенд Server Manager

Фронтенд-часть приложения для управления серверами и зонами.

## Установка

```bash
npm install
```

## Запуск приложения

```bash
npm start
```

Приложение будет доступно по адресу [http://localhost:3000](http://localhost:3000).

## Запуск тестов

Для запуска тестов можно использовать скрипт:

```bash
./run_tests.sh
```

Или запустить тесты напрямую:

```bash
npm test
```

Для запуска тестов с отчетом о покрытии:

```bash
npm test -- --coverage
```

## Структура тестов

Тесты расположены в следующих директориях:

- `src/tests/components` - тесты для компонентов
- `src/tests/services` - тесты для сервисов

## Покрытие кода тестами

После запуска тестов с флагом `--coverage` отчет о покрытии будет доступен в директории `coverage/lcov-report/index.html`.

## Технологии

- React
- TypeScript
- Material UI
- React Router
- Jest
- React Testing Library

## Технологический стек

- React + TypeScript
- Material UI для интерфейса
- PouchDB для локального хранения и синхронизации с сервером
- React Router для маршрутизации
- Formik + Yup для форм и валидации

## Установка и запуск

1. Установите зависимости:
```bash
npm install
```

2. Создайте файл `.env` с переменными окружения:
```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_COUCHDB_URL=http://localhost:5984/server_resources
```

3. Запустите приложение:
```bash
npm start
```

Или используйте скрипт:
```bash
./run.sh
```

## Структура проекта

- `src/components/` - Компоненты React
- `src/pages/` - Страницы приложения
- `src/models/` - Типы и интерфейсы TypeScript
- `src/services/` - Сервисы для работы с API и базой данных
- `src/context/` - Контексты React для управления состоянием

## Аутентификация

Для входа в приложение используйте:
- Логин: admin
- Пароль: admin
