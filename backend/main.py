from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import requests
import json
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

app = FastAPI(title="Сервис управления серверными ресурсами")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшн режиме указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Настройка подключения к PouchDB
POUCHDB_URL = os.getenv("POUCHDB_URL", "http://localhost:5984")

# Функции для работы с PouchDB через HTTP API
def create_db_if_not_exists(db_name):
    response = requests.put(f"{POUCHDB_URL}/{db_name}")
    return response.status_code == 201 or response.status_code == 412

def get_doc(db_name, doc_id):
    response = requests.get(f"{POUCHDB_URL}/{db_name}/{doc_id}")
    if response.status_code == 200:
        return response.json()
    return None

def save_doc(db_name, doc):
    if '_id' in doc:
        doc_id = doc['_id']
        existing_doc = get_doc(db_name, doc_id)
        if existing_doc:
            doc['_rev'] = existing_doc['_rev']
            response = requests.put(f"{POUCHDB_URL}/{db_name}/{doc_id}", json=doc)
        else:
            response = requests.put(f"{POUCHDB_URL}/{db_name}/{doc_id}", json=doc)
    else:
        response = requests.post(f"{POUCHDB_URL}/{db_name}", json=doc)
    
    if response.status_code in [201, 200]:
        return response.json()
    else:
        raise Exception(f"Ошибка сохранения документа: {response.text}")

def delete_doc(db_name, doc_id):
    doc = get_doc(db_name, doc_id)
    if doc:
        response = requests.delete(f"{POUCHDB_URL}/{db_name}/{doc_id}?rev={doc['_rev']}")
        return response.status_code == 200
    return False

def query_view(db_name, view_name, **params):
    response = requests.get(f"{POUCHDB_URL}/{db_name}/_design/{view_name}/_view/{view_name}", params=params)
    if response.status_code == 200:
        return response.json()
    return {"rows": []}

def get_all_docs(db_name, include_docs=True):
    params = {"include_docs": "true" if include_docs else "false"}
    response = requests.get(f"{POUCHDB_URL}/{db_name}/_all_docs", params=params)
    if response.status_code == 200:
        return response.json()
    return {"rows": []}

# Создание БД, если не существует
create_db_if_not_exists("server_resources")
create_db_if_not_exists("users")

# Настройка безопасности
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# Модели данных
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
    
class ZoneInDB(Zone):
    _id: str
    _rev: Optional[str] = None

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Функции для работы с безопасностью
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(username: str):
    user_id = f"user:{username}"
    user_data = get_doc("users", user_id)
    if user_data:
        return UserInDB(**user_data)
    return None

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Невалидные учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Пользователь неактивен")
    return current_user

# Маршруты для аутентификации
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

# Создание тестового пользователя при первом запуске
@app.on_event("startup")
async def startup_event():
    user_doc = get_doc("users", "user:admin")
    if not user_doc:
        hashed_password = get_password_hash("admin")
        user = {
            "_id": "user:admin",
            "username": "admin",
            "email": "admin@example.com",
            "full_name": "Admin User",
            "disabled": False,
            "hashed_password": hashed_password
        }
        save_doc("users", user)
        print("Создан тестовый пользователь: admin/admin")

# API для работы с зонами
@app.get("/zones/", response_model=List[Zone])
async def get_all_zones(current_user: User = Depends(get_current_active_user)):
    """Получить список всех зон"""
    zones = []
    result = get_all_docs("server_resources", include_docs=True)
    for row in result.get("rows", []):
        doc = row.get("doc", {})
        if doc.get('type') == 'zone':
            # Исключаем служебные поля PouchDB
            zone = {k: v for k, v in doc.items() if not k.startswith('_')}
            zones.append(zone)
    return zones

@app.post("/zones/", response_model=dict)
async def create_zone(zone: Zone, current_user: User = Depends(get_current_active_user)):
    """Создать новую зону"""
    # Проверяем, что зона с таким именем еще не существует
    result = get_all_docs("server_resources", include_docs=True)
    for row in result.get("rows", []):
        doc = row.get("doc", {})
        if doc.get('type') == 'zone' and doc.get('name') == zone.name:
            raise HTTPException(status_code=400, detail="Зона с таким именем уже существует")
    
    # Добавляем _id для PouchDB
    doc_id = f"zone:{zone.name}"
    zone_dict = zone.dict()
    zone_dict["_id"] = doc_id
    
    # Сохраняем в БД
    save_doc("server_resources", zone_dict)
    
    return {"message": f"Зона {zone.name} успешно создана", "id": doc_id}

@app.get("/zones/{zone_name}", response_model=Zone)
async def get_zone(zone_name: str, current_user: User = Depends(get_current_active_user)):
    """Получить зону по имени"""
    doc_id = f"zone:{zone_name}"
    zone_data = get_doc("server_resources", doc_id)
    if zone_data:
        # Исключаем служебные поля PouchDB
        zone = {k: v for k, v in zone_data.items() if not k.startswith('_')}
        return zone
    raise HTTPException(status_code=404, detail="Зона не найдена")

@app.put("/zones/{zone_name}", response_model=dict)
async def update_zone(zone_name: str, zone_update: Zone, current_user: User = Depends(get_current_active_user)):
    """Обновить зону"""
    doc_id = f"zone:{zone_name}"
    zone_data = get_doc("server_resources", doc_id)
    if zone_data:
        # Обновляем данные
        zone_dict = zone_update.dict()
        for key, value in zone_dict.items():
            zone_data[key] = value
        
        # Сохраняем обновленную зону
        save_doc("server_resources", zone_data)
        
        return {"message": f"Зона {zone_name} успешно обновлена"}
    raise HTTPException(status_code=404, detail="Зона не найдена")

@app.delete("/zones/{zone_name}", response_model=dict)
async def delete_zone(zone_name: str, current_user: User = Depends(get_current_active_user)):
    """Удалить зону"""
    doc_id = f"zone:{zone_name}"
    if delete_doc("server_resources", doc_id):
        return {"message": f"Зона {zone_name} успешно удалена"}
    raise HTTPException(status_code=404, detail="Зона не найдена")

# API для работы с окружениями
@app.post("/zones/{zone_name}/environments/", response_model=dict)
async def create_environment(
    zone_name: str,
    environment: Environment,
    current_user: User = Depends(get_current_active_user)
):
    """Добавить окружение в зону"""
    doc_id = f"zone:{zone_name}"
    zone_data = get_doc("server_resources", doc_id)
    if zone_data:
        # Проверяем, существует ли окружение с таким именем
        environments = zone_data.get("environments", [])
        for env in environments:
            if env["name"] == environment.name:
                raise HTTPException(status_code=400, detail=f"Окружение с именем {environment.name} уже существует в зоне {zone_name}")
        
        # Добавляем новое окружение
        if "environments" not in zone_data:
            zone_data["environments"] = []
        zone_data["environments"].append(environment.dict())
        
        # Сохраняем обновленную зону
        save_doc("server_resources", zone_data)
        
        return {"message": f"Окружение {environment.name} успешно добавлено в зону {zone_name}"}
    raise HTTPException(status_code=404, detail="Зона не найдена")

@app.put("/zones/{zone_name}/environments/{env_name}", response_model=dict)
async def update_environment(
    zone_name: str,
    env_name: str,
    environment: Environment,
    current_user: User = Depends(get_current_active_user)
):
    """Обновить окружение в зоне"""
    doc_id = f"zone:{zone_name}"
    zone_data = get_doc("server_resources", doc_id)
    if zone_data:
        # Проверяем, существует ли окружение с таким именем
        environments = zone_data.get("environments", [])
        env_index = None
        for i, env in enumerate(environments):
            if env["name"] == env_name:
                env_index = i
                break
        
        if env_index is None:
            raise HTTPException(status_code=404, detail=f"Окружение {env_name} не найдено в зоне {zone_name}")
        
        # Обновляем окружение
        zone_data["environments"][env_index] = environment.dict()
        
        # Сохраняем обновленную зону
        save_doc("server_resources", zone_data)
        
        return {"message": f"Окружение {env_name} успешно обновлено в зоне {zone_name}"}
    raise HTTPException(status_code=404, detail="Зона не найдена")

@app.delete("/zones/{zone_name}/environments/{env_name}", response_model=dict)
async def delete_environment(
    zone_name: str,
    env_name: str,
    current_user: User = Depends(get_current_active_user)
):
    """Удалить окружение из зоны"""
    doc_id = f"zone:{zone_name}"
    zone_data = get_doc("server_resources", doc_id)
    if zone_data:
        # Проверяем, существует ли окружение с таким именем
        environments = zone_data.get("environments", [])
        env_index = None
        for i, env in enumerate(environments):
            if env["name"] == env_name:
                env_index = i
                break
        
        if env_index is None:
            raise HTTPException(status_code=404, detail=f"Окружение {env_name} не найдено в зоне {zone_name}")
        
        # Удаляем окружение
        zone_data["environments"].pop(env_index)
        
        # Сохраняем обновленную зону
        save_doc("server_resources", zone_data)
        
        return {"message": f"Окружение {env_name} успешно удалено из зоны {zone_name}"}
    raise HTTPException(status_code=404, detail="Зона не найдена")

# API для работы с серверами
@app.post("/zones/{zone_name}/environments/{env_name}/servers/", response_model=dict)
async def add_server(
    zone_name: str,
    env_name: str,
    server: Server,
    current_user: User = Depends(get_current_active_user)
):
    """Добавить сервер в окружение"""
    doc_id = f"zone:{zone_name}"
    zone_data = get_doc("server_resources", doc_id)
    if zone_data:
        # Проверяем, существует ли окружение с таким именем
        environments = zone_data.get("environments", [])
        env_index = None
        for i, env in enumerate(environments):
            if env["name"] == env_name:
                env_index = i
                break
        
        if env_index is None:
            raise HTTPException(status_code=404, detail=f"Окружение {env_name} не найдено в зоне {zone_name}")
        
        # Проверяем, существует ли сервер с таким FQDN
        servers = zone_data["environments"][env_index].get("servers", [])
        for existing_server in servers:
            if existing_server["fqdn"] == server.fqdn:
                raise HTTPException(status_code=400, detail=f"Сервер с FQDN {server.fqdn} уже существует в окружении {env_name}")
        
        # Добавляем сервер
        if "servers" not in zone_data["environments"][env_index]:
            zone_data["environments"][env_index]["servers"] = []
        zone_data["environments"][env_index]["servers"].append(server.dict())
        
        # Сохраняем обновленную зону
        save_doc("server_resources", zone_data)
        
        return {"message": f"Сервер {server.fqdn} успешно добавлен в окружение {env_name} зоны {zone_name}"}
    raise HTTPException(status_code=404, detail="Зона не найдена")

@app.put("/zones/{zone_name}/environments/{env_name}/servers/{server_fqdn}", response_model=dict)
async def update_server(
    zone_name: str,
    env_name: str,
    server_fqdn: str,
    server: Server,
    current_user: User = Depends(get_current_active_user)
):
    """Обновить сервер в окружении"""
    doc_id = f"zone:{zone_name}"
    zone_data = get_doc("server_resources", doc_id)
    if zone_data:
        # Проверяем, существует ли окружение с таким именем
        environments = zone_data.get("environments", [])
        env_index = None
        for i, env in enumerate(environments):
            if env["name"] == env_name:
                env_index = i
                break
        
        if env_index is None:
            raise HTTPException(status_code=404, detail=f"Окружение {env_name} не найдено в зоне {zone_name}")
        
        # Проверяем, существует ли сервер с таким FQDN
        servers = zone_data["environments"][env_index].get("servers", [])
        server_index = None
        for i, s in enumerate(servers):
            if s["fqdn"] == server_fqdn:
                server_index = i
                break
        
        if server_index is None:
            raise HTTPException(status_code=404, detail=f"Сервер с FQDN {server_fqdn} не найден в окружении {env_name}")
        
        # Обновляем сервер
        zone_data["environments"][env_index]["servers"][server_index] = server.dict()
        
        # Сохраняем обновленную зону
        save_doc("server_resources", zone_data)
        
        return {"message": f"Сервер {server_fqdn} успешно обновлен в окружении {env_name} зоны {zone_name}"}
    raise HTTPException(status_code=404, detail="Зона не найдена")

@app.delete("/zones/{zone_name}/environments/{env_name}/servers/{server_fqdn}", response_model=dict)
async def delete_server(
    zone_name: str,
    env_name: str,
    server_fqdn: str,
    current_user: User = Depends(get_current_active_user)
):
    """Удалить сервер из окружения"""
    doc_id = f"zone:{zone_name}"
    zone_data = get_doc("server_resources", doc_id)
    if zone_data:
        # Проверяем, существует ли окружение с таким именем
        environments = zone_data.get("environments", [])
        env_index = None
        for i, env in enumerate(environments):
            if env["name"] == env_name:
                env_index = i
                break
        
        if env_index is None:
            raise HTTPException(status_code=404, detail=f"Окружение {env_name} не найдено в зоне {zone_name}")
        
        # Проверяем, существует ли сервер с таким FQDN
        servers = zone_data["environments"][env_index].get("servers", [])
        server_index = None
        for i, s in enumerate(servers):
            if s["fqdn"] == server_fqdn:
                server_index = i
                break
        
        if server_index is None:
            raise HTTPException(status_code=404, detail=f"Сервер с FQDN {server_fqdn} не найден в окружении {env_name}")
        
        # Удаляем сервер
        zone_data["environments"][env_index]["servers"].pop(server_index)
        
        # Сохраняем обновленную зону
        save_doc("server_resources", zone_data)
        
        return {"message": f"Сервер {server_fqdn} успешно удален из окружения {env_name} зоны {zone_name}"}
    raise HTTPException(status_code=404, detail="Зона не найдена")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
