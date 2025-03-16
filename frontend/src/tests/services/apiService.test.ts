import axios from 'axios';
import { apiService, setAuthToken } from '../../services/apiService';
import { Zone, Environment, Server } from '../../models/types';

// Мокаем axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('apiService', () => {
  // Сбрасываем моки перед каждым тестом
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
    
    // Мокаем axios.create для возврата мокнутого экземпляра axios
    mockedAxios.create.mockReturnValue(mockedAxios);
  });

  describe('setAuthToken', () => {
    it('должен устанавливать токен в заголовки и localStorage', () => {
      // Мокаем localStorage
      const setItemSpy = jest.spyOn(Storage.prototype, 'setItem');
      
      // Вызываем функцию
      setAuthToken('test-token');
      
      // Проверяем, что токен был установлен в localStorage
      expect(setItemSpy).toHaveBeenCalledWith('token', 'test-token');
      
      // Проверяем, что токен был установлен в заголовки axios
      expect(mockedAxios.defaults.headers.common['Authorization']).toBe('Bearer test-token');
    });

    it('должен удалять токен из заголовков и localStorage при передаче null', () => {
      // Мокаем localStorage
      const removeItemSpy = jest.spyOn(Storage.prototype, 'removeItem');
      
      // Вызываем функцию
      setAuthToken(null);
      
      // Проверяем, что токен был удален из localStorage
      expect(removeItemSpy).toHaveBeenCalledWith('token');
      
      // Проверяем, что токен был удален из заголовков axios
      expect(mockedAxios.defaults.headers.common['Authorization']).toBeUndefined();
    });
  });

  describe('login', () => {
    it('должен отправлять правильный запрос и возвращать данные', async () => {
      // Мокаем ответ axios
      const mockResponse = {
        data: {
          access_token: 'test-token',
          token_type: 'bearer'
        }
      };
      mockedAxios.post.mockResolvedValueOnce(mockResponse);
      
      // Вызываем функцию
      const result = await apiService.login({ username: 'test', password: 'password' });
      
      // Проверяем, что axios.post был вызван с правильными параметрами
      expect(mockedAxios.post).toHaveBeenCalledWith(
        '/token',
        expect.any(FormData),
        expect.objectContaining({
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        })
      );
      
      // Проверяем результат
      expect(result).toEqual(mockResponse.data);
    });
  });

  describe('getCurrentUser', () => {
    it('должен отправлять правильный запрос и возвращать данные', async () => {
      // Мокаем ответ axios
      const mockResponse = {
        data: {
          username: 'test',
          email: 'test@example.com',
          full_name: 'Test User'
        }
      };
      mockedAxios.get.mockResolvedValueOnce(mockResponse);
      
      // Вызываем функцию
      const result = await apiService.getCurrentUser();
      
      // Проверяем, что axios.get был вызван с правильными параметрами
      expect(mockedAxios.get).toHaveBeenCalledWith('/users/me');
      
      // Проверяем результат
      expect(result).toEqual(mockResponse.data);
    });
  });

  describe('getZones', () => {
    it('должен отправлять правильный запрос и возвращать данные', async () => {
      // Мокаем ответ axios
      const mockResponse = {
        data: [
          { name: 'zone1', type: 'zone', environments: [] },
          { name: 'zone2', type: 'zone', environments: [] }
        ]
      };
      mockedAxios.get.mockResolvedValueOnce(mockResponse);
      
      // Вызываем функцию
      const result = await apiService.getZones();
      
      // Проверяем, что axios.get был вызван с правильными параметрами
      expect(mockedAxios.get).toHaveBeenCalledWith('/zones/');
      
      // Проверяем результат
      expect(result).toEqual(mockResponse.data);
    });
  });

  describe('getZone', () => {
    it('должен отправлять правильный запрос и возвращать данные', async () => {
      // Мокаем ответ axios
      const mockResponse = {
        data: {
          name: 'zone1',
          type: 'zone',
          environments: [
            { name: 'prod', servers: [] }
          ]
        }
      };
      mockedAxios.get.mockResolvedValueOnce(mockResponse);
      
      // Вызываем функцию
      const result = await apiService.getZone('zone1');
      
      // Проверяем, что axios.get был вызван с правильными параметрами
      expect(mockedAxios.get).toHaveBeenCalledWith('/zones/zone1');
      
      // Проверяем результат
      expect(result).toEqual(mockResponse.data);
    });
  });

  describe('createZone', () => {
    it('должен отправлять правильный запрос и возвращать данные', async () => {
      // Создаем тестовую зону
      const testZone: Zone = {
        name: 'new-zone',
        type: 'zone',
        environments: []
      };
      
      // Мокаем ответ axios
      const mockResponse = {
        data: testZone
      };
      mockedAxios.post.mockResolvedValueOnce(mockResponse);
      
      // Вызываем функцию
      const result = await apiService.createZone(testZone);
      
      // Проверяем, что axios.post был вызван с правильными параметрами
      expect(mockedAxios.post).toHaveBeenCalledWith('/zones/', testZone);
      
      // Проверяем результат
      expect(result).toEqual(mockResponse.data);
    });
  });

  describe('updateZone', () => {
    it('должен отправлять правильный запрос и возвращать данные', async () => {
      // Создаем тестовую зону
      const testZone: Zone = {
        name: 'zone1',
        type: 'zone',
        environments: [
          { name: 'prod', servers: [] }
        ]
      };
      
      // Мокаем ответ axios
      const mockResponse = {
        data: testZone
      };
      mockedAxios.put.mockResolvedValueOnce(mockResponse);
      
      // Вызываем функцию
      const result = await apiService.updateZone(testZone);
      
      // Проверяем, что axios.put был вызван с правильными параметрами
      expect(mockedAxios.put).toHaveBeenCalledWith('/zones/zone1', testZone);
      
      // Проверяем результат
      expect(result).toEqual(mockResponse.data);
    });
  });

  describe('deleteZone', () => {
    it('должен отправлять правильный запрос', async () => {
      // Мокаем ответ axios
      mockedAxios.delete.mockResolvedValueOnce({});
      
      // Вызываем функцию
      await apiService.deleteZone('zone1');
      
      // Проверяем, что axios.delete был вызван с правильными параметрами
      expect(mockedAxios.delete).toHaveBeenCalledWith('/zones/zone1');
    });
  });

  describe('addEnvironment', () => {
    it('должен отправлять правильный запрос и возвращать данные', async () => {
      // Создаем тестовое окружение
      const testEnv: Environment = {
        name: 'dev',
        servers: []
      };
      
      // Мокаем ответ axios
      const mockResponse = {
        data: {
          name: 'zone1',
          type: 'zone',
          environments: [testEnv]
        }
      };
      mockedAxios.post.mockResolvedValueOnce(mockResponse);
      
      // Вызываем функцию
      const result = await apiService.addEnvironment('zone1', testEnv);
      
      // Проверяем, что axios.post был вызван с правильными параметрами
      expect(mockedAxios.post).toHaveBeenCalledWith('/zones/zone1/environments/', testEnv);
      
      // Проверяем результат
      expect(result).toEqual(mockResponse.data);
    });
  });

  describe('addServer', () => {
    it('должен отправлять правильный запрос и возвращать данные', async () => {
      // Создаем тестовый сервер
      const testServer: Server = {
        fqdn: 'server1.example.com',
        ip: '192.168.1.1',
        status: 'available',
        server_type: 'web'
      };
      
      // Мокаем ответ axios
      const mockResponse = {
        data: {
          name: 'zone1',
          type: 'zone',
          environments: [
            {
              name: 'prod',
              servers: [testServer]
            }
          ]
        }
      };
      mockedAxios.post.mockResolvedValueOnce(mockResponse);
      
      // Вызываем функцию
      const result = await apiService.addServer('zone1', 'prod', testServer);
      
      // Проверяем, что axios.post был вызван с правильными параметрами
      expect(mockedAxios.post).toHaveBeenCalledWith('/zones/zone1/environments/prod/servers/', testServer);
      
      // Проверяем результат
      expect(result).toEqual(mockResponse.data);
    });
  });
}); 