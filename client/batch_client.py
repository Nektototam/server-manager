#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import os
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

class Server(BaseModel):
    fqdn: str
    ip: str
    status: str  # "available" или "unavailable"
    server_type: str

class Environment(BaseModel):
    name: str
    servers: List[Server] = []

class Zone(BaseModel):
    name: str
    type: str = "zone"
    environments: List[Environment] = []

class BatchClient:
    """
    Клиент для пакетной работы с данными сервера управления ресурсами.
    """
    
    def __init__(self, base_url: str = None, username: str = None, password: str = None):
        """
        Инициализация клиента.
        
        Args:
            base_url: URL сервера API (по умолчанию берется из переменной окружения API_URL)
            username: Имя пользователя (по умолчанию берется из переменной окружения API_USERNAME)
            password: Пароль (по умолчанию берется из переменной окружения API_PASSWORD)
        """
        self.base_url = base_url or os.getenv("API_URL", "http://localhost:8000")
        self.username = username or os.getenv("API_USERNAME", "admin")
        self.password = password or os.getenv("API_PASSWORD", "admin")
        self.token = None
        self.headers = {}
        
    def login(self) -> bool:
        """
        Аутентификация на сервере и получение токена.
        
        Returns:
            bool: True если аутентификация успешна, иначе False
        """
        try:
            response = requests.post(
                f"{self.base_url}/token",
                data={"username": self.username, "password": self.password},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.token = token_data["access_token"]
                self.headers = {"Authorization": f"Bearer {self.token}"}
                return True
            else:
                print(f"Ошибка аутентификации: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"Ошибка при аутентификации: {str(e)}")
            return False
    
    def get_all_zones(self) -> List[Zone]:
        """
        Получение списка всех зон.
        
        Returns:
            List[Zone]: Список объектов зон
        """
        if not self.token:
            self.login()
            
        response = requests.get(f"{self.base_url}/zones/", headers=self.headers)
        
        if response.status_code == 200:
            zones_data = response.json()
            return [Zone(**zone) for zone in zones_data]
        else:
            print(f"Ошибка получения зон: {response.status_code} - {response.text}")
            return []
    
    def get_zone(self, zone_name: str) -> Optional[Zone]:
        """
        Получение информации о конкретной зоне.
        
        Args:
            zone_name: Имя зоны
            
        Returns:
            Optional[Zone]: Объект зоны или None в случае ошибки
        """
        if not self.token:
            self.login()
            
        response = requests.get(f"{self.base_url}/zones/{zone_name}", headers=self.headers)
        
        if response.status_code == 200:
            return Zone(**response.json())
        else:
            print(f"Ошибка получения зоны {zone_name}: {response.status_code} - {response.text}")
            return None
    
    def create_zone(self, zone: Zone) -> bool:
        """
        Создание новой зоны.
        
        Args:
            zone: Объект зоны для создания
            
        Returns:
            bool: True если создание успешно, иначе False
        """
        if not self.token:
            self.login()
            
        response = requests.post(
            f"{self.base_url}/zones/",
            json=zone.dict(),
            headers=self.headers
        )
        
        if response.status_code in [200, 201]:
            return True
        else:
            print(f"Ошибка создания зоны: {response.status_code} - {response.text}")
            return False
    
    def update_zone(self, zone_name: str, zone: Zone) -> bool:
        """
        Обновление существующей зоны.
        
        Args:
            zone_name: Имя зоны для обновления
            zone: Новые данные зоны
            
        Returns:
            bool: True если обновление успешно, иначе False
        """
        if not self.token:
            self.login()
            
        response = requests.put(
            f"{self.base_url}/zones/{zone_name}",
            json=zone.dict(),
            headers=self.headers
        )
        
        if response.status_code == 200:
            return True
        else:
            print(f"Ошибка обновления зоны {zone_name}: {response.status_code} - {response.text}")
            return False
    
    def delete_zone(self, zone_name: str) -> bool:
        """
        Удаление зоны.
        
        Args:
            zone_name: Имя зоны для удаления
            
        Returns:
            bool: True если удаление успешно, иначе False
        """
        if not self.token:
            self.login()
            
        response = requests.delete(f"{self.base_url}/zones/{zone_name}", headers=self.headers)
        
        if response.status_code == 200:
            return True
        else:
            print(f"Ошибка удаления зоны {zone_name}: {response.status_code} - {response.text}")
            return False
    
    def create_environment(self, zone_name: str, environment: Environment) -> bool:
        """
        Создание окружения в зоне.
        
        Args:
            zone_name: Имя зоны
            environment: Объект окружения для создания
            
        Returns:
            bool: True если создание успешно, иначе False
        """
        if not self.token:
            self.login()
            
        response = requests.post(
            f"{self.base_url}/zones/{zone_name}/environments/",
            json=environment.dict(),
            headers=self.headers
        )
        
        if response.status_code in [200, 201]:
            return True
        else:
            print(f"Ошибка создания окружения в зоне {zone_name}: {response.status_code} - {response.text}")
            return False
    
    def update_environment(self, zone_name: str, env_name: str, environment: Environment) -> bool:
        """
        Обновление окружения в зоне.
        
        Args:
            zone_name: Имя зоны
            env_name: Имя окружения для обновления
            environment: Новые данные окружения
            
        Returns:
            bool: True если обновление успешно, иначе False
        """
        if not self.token:
            self.login()
            
        response = requests.put(
            f"{self.base_url}/zones/{zone_name}/environments/{env_name}",
            json=environment.dict(),
            headers=self.headers
        )
        
        if response.status_code == 200:
            return True
        else:
            print(f"Ошибка обновления окружения {env_name} в зоне {zone_name}: {response.status_code} - {response.text}")
            return False
    
    def delete_environment(self, zone_name: str, env_name: str) -> bool:
        """
        Удаление окружения из зоны.
        
        Args:
            zone_name: Имя зоны
            env_name: Имя окружения для удаления
            
        Returns:
            bool: True если удаление успешно, иначе False
        """
        if not self.token:
            self.login()
            
        response = requests.delete(
            f"{self.base_url}/zones/{zone_name}/environments/{env_name}",
            headers=self.headers
        )
        
        if response.status_code == 200:
            return True
        else:
            print(f"Ошибка удаления окружения {env_name} из зоны {zone_name}: {response.status_code} - {response.text}")
            return False
    
    def add_server(self, zone_name: str, env_name: str, server: Server) -> bool:
        """
        Добавление сервера в окружение.
        
        Args:
            zone_name: Имя зоны
            env_name: Имя окружения
            server: Объект сервера для добавления
            
        Returns:
            bool: True если добавление успешно, иначе False
        """
        if not self.token:
            self.login()
            
        response = requests.post(
            f"{self.base_url}/zones/{zone_name}/environments/{env_name}/servers/",
            json=server.dict(),
            headers=self.headers
        )
        
        if response.status_code in [200, 201]:
            return True
        else:
            print(f"Ошибка добавления сервера в окружение {env_name} зоны {zone_name}: {response.status_code} - {response.text}")
            return False
    
    def update_server(self, zone_name: str, env_name: str, server_fqdn: str, server: Server) -> bool:
        """
        Обновление сервера в окружении.
        
        Args:
            zone_name: Имя зоны
            env_name: Имя окружения
            server_fqdn: FQDN сервера для обновления
            server: Новые данные сервера
            
        Returns:
            bool: True если обновление успешно, иначе False
        """
        if not self.token:
            self.login()
            
        response = requests.put(
            f"{self.base_url}/zones/{zone_name}/environments/{env_name}/servers/{server_fqdn}",
            json=server.dict(),
            headers=self.headers
        )
        
        if response.status_code == 200:
            return True
        else:
            print(f"Ошибка обновления сервера {server_fqdn} в окружении {env_name} зоны {zone_name}: {response.status_code} - {response.text}")
            return False
    
    def delete_server(self, zone_name: str, env_name: str, server_fqdn: str) -> bool:
        """
        Удаление сервера из окружения.
        
        Args:
            zone_name: Имя зоны
            env_name: Имя окружения
            server_fqdn: FQDN сервера для удаления
            
        Returns:
            bool: True если удаление успешно, иначе False
        """
        if not self.token:
            self.login()
            
        response = requests.delete(
            f"{self.base_url}/zones/{zone_name}/environments/{env_name}/servers/{server_fqdn}",
            headers=self.headers
        )
        
        if response.status_code == 200:
            return True
        else:
            print(f"Ошибка удаления сервера {server_fqdn} из окружения {env_name} зоны {zone_name}: {response.status_code} - {response.text}")
            return False
    
    def batch_create_zones(self, zones: List[Zone]) -> Dict[str, bool]:
        """
        Пакетное создание зон.
        
        Args:
            zones: Список объектов зон для создания
            
        Returns:
            Dict[str, bool]: Словарь с результатами создания для каждой зоны
        """
        results = {}
        for zone in zones:
            results[zone.name] = self.create_zone(zone)
        return results
    
    def batch_create_environments(self, zone_name: str, environments: List[Environment]) -> Dict[str, bool]:
        """
        Пакетное создание окружений в зоне.
        
        Args:
            zone_name: Имя зоны
            environments: Список объектов окружений для создания
            
        Returns:
            Dict[str, bool]: Словарь с результатами создания для каждого окружения
        """
        results = {}
        for env in environments:
            results[env.name] = self.create_environment(zone_name, env)
        return results
    
    def batch_add_servers(self, zone_name: str, env_name: str, servers: List[Server]) -> Dict[str, bool]:
        """
        Пакетное добавление серверов в окружение.
        
        Args:
            zone_name: Имя зоны
            env_name: Имя окружения
            servers: Список объектов серверов для добавления
            
        Returns:
            Dict[str, bool]: Словарь с результатами добавления для каждого сервера
        """
        results = {}
        for server in servers:
            results[server.fqdn] = self.add_server(zone_name, env_name, server)
        return results
    
    def import_from_json(self, json_file: str) -> Dict[str, Any]:
        """
        Импорт данных из JSON-файла.
        
        Args:
            json_file: Путь к JSON-файлу с данными
            
        Returns:
            Dict[str, Any]: Словарь с результатами импорта
        """
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            results = {
                "zones": {},
                "environments": {},
                "servers": {}
            }
            
            # Импорт зон
            if "zones" in data:
                for zone_data in data["zones"]:
                    zone = Zone(**zone_data)
                    results["zones"][zone.name] = self.create_zone(zone)
                    
                    # Импорт окружений для зоны
                    if "environments" in zone_data:
                        results["environments"][zone.name] = {}
                        for env_data in zone_data["environments"]:
                            env = Environment(**env_data)
                            results["environments"][zone.name][env.name] = self.create_environment(zone.name, env)
                            
                            # Импорт серверов для окружения
                            if "servers" in env_data:
                                results["servers"][f"{zone.name}/{env.name}"] = {}
                                for server_data in env_data["servers"]:
                                    server = Server(**server_data)
                                    results["servers"][f"{zone.name}/{env.name}"][server.fqdn] = self.add_server(zone.name, env.name, server)
            
            return results
        except Exception as e:
            print(f"Ошибка при импорте из JSON: {str(e)}")
            return {"error": str(e)}
    
    def export_to_json(self, output_file: str) -> bool:
        """
        Экспорт всех данных в JSON-файл.
        
        Args:
            output_file: Путь к файлу для сохранения данных
            
        Returns:
            bool: True если экспорт успешен, иначе False
        """
        try:
            zones = self.get_all_zones()
            data = {"zones": []}
            
            for zone in zones:
                zone_dict = zone.dict()
                data["zones"].append(zone_dict)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Ошибка при экспорте в JSON: {str(e)}")
            return False


if __name__ == "__main__":
    # Пример использования клиента
    client = BatchClient()
    
    # Аутентификация
    if client.login():
        print("Аутентификация успешна")
        
        # Получение списка зон
        zones = client.get_all_zones()
        print(f"Найдено зон: {len(zones)}")
        
        # Пример создания новой зоны
        new_zone = Zone(name="test-zone", environments=[
            Environment(name="dev", servers=[
                Server(fqdn="server1.dev.example.com", ip="192.168.1.1", status="available", server_type="web"),
                Server(fqdn="server2.dev.example.com", ip="192.168.1.2", status="available", server_type="db")
            ]),
            Environment(name="prod", servers=[
                Server(fqdn="server1.prod.example.com", ip="10.0.0.1", status="available", server_type="web"),
                Server(fqdn="server2.prod.example.com", ip="10.0.0.2", status="available", server_type="db")
            ])
        ])
        
        # Раскомментируйте для тестирования
        # if client.create_zone(new_zone):
        #     print(f"Зона {new_zone.name} успешно создана")
        
        # Экспорт данных в JSON
        # if client.export_to_json("export.json"):
        #     print("Данные успешно экспортированы в export.json")
    else:
        print("Ошибка аутентификации") 