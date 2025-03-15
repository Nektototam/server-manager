#!/usr/bin/env python
import requests
import json
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

# Основная функция
def main():
    print("Проверка данных приложения")
    
    # Получение токена
    token = get_token()
    print(f"Токен получен: {token[:10]}...")
    
    # Получение списка всех зон
    zones = get_all_zones(token)
    print(f"Количество зон: {len(zones)}")
    
    # Вывод информации о зонах
    for zone in zones:
        zone_name = zone["name"]
        zone_data = get_zone(token, zone_name)
        environments = zone_data.get("environments", [])
        print(f"Зона: {zone_name}, окружений: {len(environments)}")
        
        # Вывод информации об окружениях
        for env in environments:
            env_name = env["name"]
            servers = env.get("servers", [])
            print(f"  Окружение: {env_name}, серверов: {len(servers)}")
            
            # Вывод информации о серверах
            for server in servers:
                print(f"    Сервер: {server['fqdn']}, IP: {server['ip']}, тип: {server['server_type']}, статус: {server['status']}")
    
    print("Проверка данных завершена!")

if __name__ == "__main__":
    main() 