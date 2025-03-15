#!/usr/bin/env python
import requests
import json
import time
import random
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Настройки
API_URL = "http://localhost:8000"
USERNAME = "admin"
PASSWORD = "admin"

# Функция для получения токена
def get_token():
    response = requests.post(
        f"{API_URL}/token",
        data={"username": USERNAME, "password": PASSWORD},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Ошибка аутентификации: {response.status_code}")
        print(response.text)
        exit(1)

# Функция для получения списка всех зон
def get_all_zones(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/zones/", headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Ошибка при получении списка зон: {response.status_code}")
        print(response.text)
        return []

# Функция для проверки существования зоны
def zone_exists(token, zone_name):
    zones = get_all_zones(token)
    for zone in zones:
        if zone.get('name') == zone_name:
            return True
    return False

# Функция для создания зоны
def create_zone(token, name):
    headers = {"Authorization": f"Bearer {token}"}
    data = {"name": name, "type": "zone", "environments": []}
    
    # Проверяем, существует ли уже зона
    if zone_exists(token, name):
        print(f"Зона '{name}' уже существует")
        return True
    
    response = requests.post(f"{API_URL}/zones/", json=data, headers=headers)
    
    if response.status_code == 200:
        print(f"Зона '{name}' успешно создана")
        # Ждем, чтобы убедиться, что зона сохранена
        time.sleep(1)
        return True
    else:
        print(f"Ошибка при создании зоны '{name}': {response.status_code}")
        print(response.text)
        return False

# Функция для получения информации о зоне
def get_zone(token, zone_name):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/zones/{zone_name}", headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Ошибка при получении информации о зоне '{zone_name}': {response.status_code}")
        print(response.text)
        return None

# Функция для создания окружения
def create_environment(token, zone_name, env_name):
    headers = {"Authorization": f"Bearer {token}"}
    data = {"name": env_name, "servers": []}
    
    # Проверяем, существует ли зона
    zone_data = get_zone(token, zone_name)
    if not zone_data:
        print(f"Зона '{zone_name}' не найдена, невозможно создать окружение '{env_name}'")
        return False
    
    # Проверяем, существует ли уже окружение
    for env in zone_data.get('environments', []):
        if env.get('name') == env_name:
            print(f"Окружение '{env_name}' уже существует в зоне '{zone_name}'")
            return True
    
    response = requests.post(
        f"{API_URL}/zones/{zone_name}/environments/", 
        json=data, 
        headers=headers
    )
    
    if response.status_code == 200:
        print(f"Окружение '{env_name}' успешно создано в зоне '{zone_name}'")
        # Ждем, чтобы убедиться, что окружение сохранено
        time.sleep(1)
        return True
    else:
        print(f"Ошибка при создании окружения '{env_name}' в зоне '{zone_name}': {response.status_code}")
        print(response.text)
        return False

# Функция для создания сервера
def create_server(token, zone_name, env_name, server_data):
    headers = {"Authorization": f"Bearer {token}"}
    
    # Проверяем, существует ли зона и окружение
    zone_data = get_zone(token, zone_name)
    if not zone_data:
        print(f"Зона '{zone_name}' не найдена, невозможно создать сервер '{server_data['fqdn']}'")
        return False
    
    env_exists = False
    for env in zone_data.get('environments', []):
        if env.get('name') == env_name:
            env_exists = True
            # Проверяем, существует ли уже сервер
            for server in env.get('servers', []):
                if server.get('fqdn') == server_data['fqdn']:
                    print(f"Сервер '{server_data['fqdn']}' уже существует в окружении '{env_name}' зоны '{zone_name}'")
                    return True
            break
    
    if not env_exists:
        print(f"Окружение '{env_name}' не найдено в зоне '{zone_name}', невозможно создать сервер '{server_data['fqdn']}'")
        return False
    
    response = requests.post(
        f"{API_URL}/zones/{zone_name}/environments/{env_name}/servers/", 
        json=server_data, 
        headers=headers
    )
    
    if response.status_code == 200:
        print(f"Сервер '{server_data['fqdn']}' успешно создан в окружении '{env_name}' зоны '{zone_name}'")
        # Ждем, чтобы убедиться, что сервер сохранен
        time.sleep(0.5)
        return True
    else:
        print(f"Ошибка при создании сервера '{server_data['fqdn']}' в окружении '{env_name}' зоны '{zone_name}': {response.status_code}")
        print(response.text)
        return False

# Функция для генерации случайного IP-адреса
def generate_random_ip():
    return f"{random.randint(10, 192)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"

# Функция для генерации данных сервера
def generate_server_data(zone, env, index):
    server_types = ["application", "database", "web", "cache", "auth"]
    statuses = ["available", "unavailable"]
    
    return {
        "fqdn": f"server-{zone}-{env}-{index}.example.com",
        "ip": generate_random_ip(),
        "status": random.choice(statuses),
        "server_type": random.choice(server_types)
    }

# Основная функция
def main():
    print("Генерация тестовых данных для приложения управления серверами")
    
    # Получение токена
    token = get_token()
    print(f"Токен получен: {token[:10]}...")
    
    # Создание зон
    zones = ["prod", "uat", "qa"]
    for zone in zones:
        create_zone(token, zone)
    
    # Ждем, чтобы убедиться, что зоны сохранены
    print("Ожидание сохранения зон...")
    time.sleep(2)
    
    # Создание областей в qa
    qa_environments = ["i_0", "i_1", "abracadabra"]
    for env in qa_environments:
        create_environment(token, "qa", env)
    
    # Ждем, чтобы убедиться, что окружения сохранены
    print("Ожидание сохранения окружений...")
    time.sleep(2)
    
    # Создание серверов в prod и uat (без областей)
    for zone in ["prod", "uat"]:
        # Создаем окружение "default" для зон без областей
        create_environment(token, zone, "default")
        
        # Ждем, чтобы убедиться, что окружение сохранено
        time.sleep(1)
        
        # Добавляем серверы
        for i in range(1, 6):  # 5 серверов
            server_data = generate_server_data(zone, "default", i)
            create_server(token, zone, "default", server_data)
    
    # Создание серверов в qa (в областях)
    for env in qa_environments:
        for i in range(1, 6):  # 5 серверов в каждой области
            server_data = generate_server_data("qa", env, i)
            create_server(token, "qa", env, server_data)
    
    print("Генерация тестовых данных завершена!")

if __name__ == "__main__":
    main() 