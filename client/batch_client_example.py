#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from batch_client import BatchClient, Zone, Environment, Server

def main():
    """
    Пример использования BatchClient для пакетной работы с данными.
    """
    # Инициализация клиента
    client = BatchClient(
        base_url="http://localhost:8000",  # URL API сервера
        username="admin",                  # Имя пользователя
        password="admin"                   # Пароль
    )
    
    # Аутентификация
    if not client.login():
        print("Ошибка аутентификации")
        return
    
    print("Аутентификация успешна")
    
    # Получение списка всех зон
    zones = client.get_all_zones()
    print(f"Найдено зон: {len(zones)}")
    for zone in zones:
        print(f"- {zone.name}")
    
    # Пример пакетного создания зон
    test_zones = [
        Zone(name="test-zone-1", environments=[]),
        Zone(name="test-zone-2", environments=[]),
        Zone(name="test-zone-3", environments=[])
    ]
    
    print("\nПакетное создание зон...")
    results = client.batch_create_zones(test_zones)
    for zone_name, success in results.items():
        print(f"Создание зоны {zone_name}: {'Успешно' if success else 'Ошибка'}")
    
    # Пример пакетного создания окружений
    test_environments = [
        Environment(name="dev", servers=[]),
        Environment(name="test", servers=[]),
        Environment(name="prod", servers=[])
    ]
    
    print("\nПакетное создание окружений в зоне test-zone-1...")
    results = client.batch_create_environments("test-zone-1", test_environments)
    for env_name, success in results.items():
        print(f"Создание окружения {env_name}: {'Успешно' if success else 'Ошибка'}")
    
    # Пример пакетного добавления серверов
    test_servers = [
        Server(fqdn="server1.dev.example.com", ip="192.168.1.1", status="available", server_type="web"),
        Server(fqdn="server2.dev.example.com", ip="192.168.1.2", status="available", server_type="db"),
        Server(fqdn="server3.dev.example.com", ip="192.168.1.3", status="available", server_type="app")
    ]
    
    print("\nПакетное добавление серверов в окружение dev зоны test-zone-1...")
    results = client.batch_add_servers("test-zone-1", "dev", test_servers)
    for server_fqdn, success in results.items():
        print(f"Добавление сервера {server_fqdn}: {'Успешно' if success else 'Ошибка'}")
    
    # Пример экспорта данных в JSON
    print("\nЭкспорт данных в JSON...")
    if client.export_to_json("export.json"):
        print("Данные успешно экспортированы в export.json")
    else:
        print("Ошибка при экспорте данных")
    
    # Пример импорта данных из JSON
    print("\nИмпорт данных из JSON...")
    results = client.import_from_json("export.json")
    print("Результаты импорта:")
    print(f"- Зоны: {len(results.get('zones', {}))} обработано")
    print(f"- Окружения: {sum(len(envs) for envs in results.get('environments', {}).values())} обработано")
    print(f"- Серверы: {sum(len(servers) for servers in results.get('servers', {}).values())} обработано")
    
    # Пример удаления данных
    print("\nУдаление тестовых данных...")
    
    # Удаление серверов
    for server in test_servers:
        if client.delete_server("test-zone-1", "dev", server.fqdn):
            print(f"Сервер {server.fqdn} удален")
    
    # Удаление окружений
    for env in test_environments:
        if client.delete_environment("test-zone-1", env.name):
            print(f"Окружение {env.name} удалено")
    
    # Удаление зон
    for zone in test_zones:
        if client.delete_zone(zone.name):
            print(f"Зона {zone.name} удалена")
    
    print("\nГотово!")

if __name__ == "__main__":
    main() 