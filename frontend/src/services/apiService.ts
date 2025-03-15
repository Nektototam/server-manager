import axios from 'axios';
import { Zone, Environment, Server, LoginRequest, AuthResponse, User } from '../models/types';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Создаем экземпляр axios с базовым URL
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Добавление интерцептора для добавления токена
export const setAuthToken = (token: string | null) => {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    // Сохраняем токен в localStorage
    localStorage.setItem('token', token);
  } else {
    delete api.defaults.headers.common['Authorization'];
    // Удаляем токен из localStorage
    localStorage.removeItem('token');
  }
};

// Попытка восстановить токен из localStorage при инициализации
const token = localStorage.getItem('token');
if (token) {
  setAuthToken(token);
}

// Сервис для работы с API
export const apiService = {
  // Аутентификация
  login: async (credentials: LoginRequest): Promise<AuthResponse> => {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    
    const response = await api.post<AuthResponse>('/token', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    
    return response.data;
  },
  
  // Получение информации о текущем пользователе
  getCurrentUser: async (): Promise<User> => {
    const response = await api.get<User>('/users/me');
    return response.data;
  },
  
  // Получение всех зон
  getZones: async (): Promise<Zone[]> => {
    const response = await api.get<Zone[]>('/zones/');
    return response.data;
  },
  
  // Получение зоны по имени
  getZone: async (zoneName: string): Promise<Zone> => {
    const response = await api.get<Zone>(`/zones/${zoneName}`);
    return response.data;
  },
  
  // Создание новой зоны
  createZone: async (zone: Zone): Promise<Zone> => {
    const response = await api.post<Zone>('/zones/', zone);
    return response.data;
  },
  
  // Обновление зоны
  updateZone: async (zone: Zone): Promise<Zone> => {
    const response = await api.put<Zone>(`/zones/${zone.name}`, zone);
    return response.data;
  },
  
  // Удаление зоны
  deleteZone: async (zoneName: string): Promise<void> => {
    await api.delete(`/zones/${zoneName}`);
  },
  
  // Создание окружения в зоне
  addEnvironment: async (zoneName: string, environment: Environment): Promise<Zone> => {
    const response = await api.post<Zone>(`/zones/${zoneName}/environments/`, environment);
    return response.data;
  },
  
  // Обновление окружения
  updateEnvironment: async (zoneName: string, envName: string, environment: Environment): Promise<Zone> => {
    const response = await api.put<Zone>(`/zones/${zoneName}/environments/${envName}`, environment);
    return response.data;
  },
  
  // Удаление окружения
  deleteEnvironment: async (zoneName: string, envName: string): Promise<Zone> => {
    const response = await api.delete<Zone>(`/zones/${zoneName}/environments/${envName}`);
    return response.data;
  },
  
  // Добавление сервера в окружение
  addServer: async (zoneName: string, envName: string, server: Server): Promise<Zone> => {
    const response = await api.post<Zone>(`/zones/${zoneName}/environments/${envName}/servers/`, server);
    return response.data;
  },
  
  // Обновление сервера
  updateServer: async (zoneName: string, envName: string, serverFqdn: string, server: Server): Promise<Zone> => {
    const response = await api.put<Zone>(`/zones/${zoneName}/environments/${envName}/servers/${serverFqdn}`, server);
    return response.data;
  },
  
  // Удаление сервера
  deleteServer: async (zoneName: string, envName: string, serverFqdn: string): Promise<Zone> => {
    const response = await api.delete<Zone>(`/zones/${zoneName}/environments/${envName}/servers/${serverFqdn}`);
    return response.data;
  },
}; 