# Клиент для пакетной работы с данными

Этот модуль предоставляет клиент для пакетной работы с данными сервера управления ресурсами.

## Возможности

- Аутентификация на сервере
- Получение списка зон, окружений и серверов
- Создание, обновление и удаление зон, окружений и серверов
- Пакетное создание зон, окружений и серверов
- Импорт данных из JSON-файла
- Экспорт данных в JSON-файл

## Установка

Для работы клиента необходимо установить зависимости:

```bash
pip install -r requirements.txt
```

## Использование

### Базовое использование

```python
from batch_client import BatchClient, Zone, Environment, Server

# Инициализация клиента
client = BatchClient(
    base_url="http://localhost:8000",
    username="admin",
    password="admin"
)

# Аутентификация
if client.login():
    # Получение списка зон
    zones = client.get_all_zones()
    print(f"Найдено зон: {len(zones)}")
    
    # Создание новой зоны
    new_zone = Zone(name="test-zone", environments=[])
    if client.create_zone(new_zone):
        print(f"Зона {new_zone.name} успешно создана")
```

### Пакетные операции

```python
# Пакетное создание зон
zones = [
    Zone(name="zone1", environments=[]),
    Zone(name="zone2", environments=[]),
    Zone(name="zone3", environments=[])
]
results = client.batch_create_zones(zones)

# Пакетное создание окружений
environments = [
    Environment(name="dev", servers=[]),
    Environment(name="test", servers=[]),
    Environment(name="prod", servers=[])
]
results = client.batch_create_environments("zone1", environments)

# Пакетное добавление серверов
servers = [
    Server(fqdn="server1.dev.example.com", ip="192.168.1.1", status="available", server_type="web"),
    Server(fqdn="server2.dev.example.com", ip="192.168.1.2", status="available", server_type="db")
]
results = client.batch_add_servers("zone1", "dev", servers)
```

### Импорт и экспорт данных

```python
# Экспорт данных в JSON
client.export_to_json("export.json")

# Импорт данных из JSON
results = client.import_from_json("export.json")
```

## Пример использования

Для запуска примера использования клиента выполните:

```bash
python batch_client_example.py
```

Или используйте скрипт:

```bash
./run_batch_client.sh
```

## Тестирование

Клиент покрыт автоматическими тестами с использованием pytest. Для запуска тестов выполните:

```bash
pytest tests/ -v
```

Или используйте скрипт для запуска тестов с отчетом о покрытии:

```bash
./run_tests.sh
```

После запуска тестов будет создан отчет о покрытии кода в директории `htmlcov/`.

## Структура JSON для импорта/экспорта

```json
{
  "zones": [
    {
      "name": "zone1",
      "type": "zone",
      "environments": [
        {
          "name": "dev",
          "servers": [
            {
              "fqdn": "server1.dev.example.com",
              "ip": "192.168.1.1",
              "status": "available",
              "server_type": "web"
            }
          ]
        }
      ]
    }
  ]
}
```

## Переменные окружения

Клиент может использовать следующие переменные окружения:

- `API_URL` - URL сервера API (по умолчанию: http://localhost:8000)
- `API_USERNAME` - Имя пользователя (по умолчанию: admin)
- `API_PASSWORD` - Пароль (по умолчанию: admin)

Вы можете создать файл `.env` в директории с клиентом:

```
API_URL=http://localhost:8000
API_USERNAME=admin
API_PASSWORD=admin
``` 