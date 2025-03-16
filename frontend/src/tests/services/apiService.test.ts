import axios from 'axios';
import { Zone, Environment, Server } from '../../models/types';

// Мокаем axios
jest.mock('axios', () => ({
  create: jest.fn(() => ({
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
    defaults: {
      headers: {
        common: {}
      }
    }
  }))
}));

// Импортируем apiService после мокирования axios
const { apiService, setAuthToken } = require('../../services/apiService');

describe('apiService', () => {
  // Получаем мокнутый экземпляр axios
  const api = axios.create();
  
  // Сбрасываем моки перед каждым тестом
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  describe('setAuthToken', () => {
    it('должен устанавливать и удалять токен в localStorage', () => {
      // Мокаем localStorage
      const setItemSpy = jest.spyOn(Storage.prototype, 'setItem');
      const removeItemSpy = jest.spyOn(Storage.prototype, 'removeItem');
      
      // Вызываем функцию для установки токена
      setAuthToken('test-token');
      
      // Проверяем, что токен был установлен в localStorage
      expect(setItemSpy).toHaveBeenCalledWith('token', 'test-token');
      
      // Вызываем функцию для удаления токена
      setAuthToken(null);
      
      // Проверяем, что токен был удален из localStorage
      expect(removeItemSpy).toHaveBeenCalledWith('token');
    });
  });

  describe('API методы', () => {
    it('должен иметь все необходимые методы', () => {
      // Проверяем наличие всех методов
      expect(apiService.login).toBeDefined();
      expect(apiService.getCurrentUser).toBeDefined();
      expect(apiService.getZones).toBeDefined();
      expect(apiService.getZone).toBeDefined();
      expect(apiService.createZone).toBeDefined();
      expect(apiService.updateZone).toBeDefined();
      expect(apiService.deleteZone).toBeDefined();
      expect(apiService.addEnvironment).toBeDefined();
      expect(apiService.updateEnvironment).toBeDefined();
      expect(apiService.deleteEnvironment).toBeDefined();
      expect(apiService.addServer).toBeDefined();
      expect(apiService.updateServer).toBeDefined();
      expect(apiService.deleteServer).toBeDefined();
    });
  });
}); 