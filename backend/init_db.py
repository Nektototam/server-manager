import requests
import json
import os
from passlib.context import CryptContext
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Настройка подключения к PouchDB
POUCHDB_URL = os.getenv("POUCHDB_URL", "http://localhost:5984")

# Настройка безопасности
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_db_if_not_exists(db_name):
    response = requests.put(f"{POUCHDB_URL}/{db_name}")
    return response.status_code == 201 or response.status_code == 412

def save_doc(db_name, doc):
    if '_id' in doc:
        doc_id = doc['_id']
        response = requests.put(f"{POUCHDB_URL}/{db_name}/{doc_id}", json=doc)
    else:
        response = requests.post(f"{POUCHDB_URL}/{db_name}", json=doc)
    
    if response.status_code in [201, 200]:
        return response.json()
    else:
        print(f"Ошибка сохранения документа: {response.text}")
        return None

def get_doc(db_name, doc_id):
    response = requests.get(f"{POUCHDB_URL}/{db_name}/{doc_id}")
    if response.status_code == 200:
        return response.json()
    return None

def create_test_users():
    print("Создание тестовых пользователей...")
    
    # Создание базы данных пользователей
    create_db_if_not_exists("users")
    
    # Создание тестового пользователя admin
    admin_user = {
        "_id": "user:admin",
        "username": "admin",
        "email": "admin@example.com",
        "full_name": "Administrator",
        "disabled": False,
        "hashed_password": pwd_context.hash("admin123")
    }
    
    # Сохранение пользователя
    result = save_doc("users", admin_user)
    if result:
        print(f"Пользователь admin создан: {result}")
    else:
        print("Ошибка при создании пользователя admin")

def create_test_zones():
    print("Создание тестовых зон и окружений...")
    
    # Создание базы данных ресурсов
    create_db_if_not_exists("server_resources")
    
    # Создание тестовой зоны Production
    prod_zone = {
        "_id": "zone:production",
        "name": "production",
        "type": "zone",
        "environments": [
            {
                "name": "main",
                "servers": [
                    {
                        "fqdn": "prod-server1.example.com",
                        "ip": "10.0.1.1",
                        "status": "available",
                        "server_type": "application"
                    },
                    {
                        "fqdn": "prod-server2.example.com",
                        "ip": "10.0.1.2",
                        "status": "available",
                        "server_type": "database"
                    }
                ]
            }
        ]
    }
    
    # Создание тестовой зоны Testing
    test_zone = {
        "_id": "zone:testing",
        "name": "testing",
        "type": "zone",
        "environments": [
            {
                "name": "qa",
                "servers": [
                    {
                        "fqdn": "qa-server1.example.com",
                        "ip": "10.0.2.1",
                        "status": "available",
                        "server_type": "application"
                    }
                ]
            },
            {
                "name": "staging",
                "servers": [
                    {
                        "fqdn": "staging-server1.example.com",
                        "ip": "10.0.2.10",
                        "status": "available",
                        "server_type": "application"
                    }
                ]
            }
        ]
    }
    
    # Сохранение зон
    result1 = save_doc("server_resources", prod_zone)
    result2 = save_doc("server_resources", test_zone)
    
    if result1:
        print(f"Зона Production создана: {result1}")
    else:
        print("Ошибка при создании зоны Production")
        
    if result2:
        print(f"Зона Testing создана: {result2}")
    else:
        print("Ошибка при создании зоны Testing")

if __name__ == "__main__":
    print("Инициализация базы данных...")
    create_test_users()
    create_test_zones()
    print("Инициализация базы данных завершена.") 