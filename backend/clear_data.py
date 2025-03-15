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

# Функция для удаления зоны
def delete_zone(token, zone_name):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(f"{API_URL}/zones/{zone_name}", headers=headers)
    
    if response.status_code == 200:
        print(f"Зона '{zone_name}' успешно удалена")
        return True
    else:
        print(f"Ошибка при удалении зоны '{zone_name}': {response.status_code}")
        print(response.text)
        return False

# Основная функция
def main():
    print("Очистка всех данных приложения")
    
    # Получение токена
    token = get_token()
    print(f"Токен получен: {token[:10]}...")
    
    # Получение списка всех зон
    zones = get_all_zones(token)
    
    if not zones:
        print("Нет зон для удаления")
        return
    
    # Удаление всех зон
    for zone in zones:
        delete_zone(token, zone["name"])
    
    print("Очистка данных завершена!")

if __name__ == "__main__":
    main() 