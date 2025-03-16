import { dbService } from '../../services/dbService';
import { apiService } from '../../services/apiService';
import { Zone, Server } from '../../models/types';

// Мокаем apiService
jest.mock('../../services/apiService', () => ({
  apiService: {
    getZones: jest.fn(),
    getZone: jest.fn(),
    createZone: jest.fn(),
    updateZone: jest.fn(),
    deleteZone: jest.fn(),
    addEnvironment: jest.fn(),
    updateEnvironment: jest.fn(),
    deleteEnvironment: jest.fn(),
    addServer: jest.fn(),
    updateServer: jest.fn(),
    deleteServer: jest.fn()
  }
}));

describe('dbService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('методы', () => {
    it('должен иметь все необходимые методы', () => {
      expect(dbService.getZones).toBeDefined();
      expect(dbService.getZone).toBeDefined();
      expect(dbService.createZone).toBeDefined();
      expect(dbService.updateZone).toBeDefined();
      expect(dbService.deleteZone).toBeDefined();
      expect(dbService.addEnvironment).toBeDefined();
      expect(dbService.updateEnvironment).toBeDefined();
      expect(dbService.deleteEnvironment).toBeDefined();
      expect(dbService.addServer).toBeDefined();
      expect(dbService.updateServer).toBeDefined();
      expect(dbService.deleteServer).toBeDefined();
    });
  });

  describe('getZones', () => {
    it('должен вызывать apiService.getZones', async () => {
      const mockZones = [{ name: 'zone1', type: 'zone', environments: [] }];
      (apiService.getZones as jest.Mock).mockResolvedValue(mockZones);

      const result = await dbService.getZones();
      
      expect(apiService.getZones).toHaveBeenCalled();
      expect(result).toEqual(mockZones);
    });

    it('должен обрабатывать ошибки при получении зон', async () => {
      // Мокаем ошибку
      const mockError = new Error('API error');
      (apiService.getZones as jest.Mock).mockRejectedValueOnce(mockError);
      
      // Проверяем, что функция выбрасывает ошибку
      await expect(dbService.getZones()).rejects.toThrow(mockError);
    });
  });

  describe('getZone', () => {
    it('должен вызывать apiService.getZone с правильными параметрами', async () => {
      const mockZone = { name: 'zone1', type: 'zone', environments: [] };
      (apiService.getZone as jest.Mock).mockResolvedValue(mockZone);

      const result = await dbService.getZone('zone1');
      
      expect(apiService.getZone).toHaveBeenCalledWith('zone1');
      expect(result).toEqual(mockZone);
    });

    it('должен возвращать null при ошибке получения зоны', async () => {
      // Мокаем ошибку
      const mockError = new Error('API error');
      (apiService.getZone as jest.Mock).mockRejectedValueOnce(mockError);
      
      // Вызываем функцию
      const result = await dbService.getZone('zone1');
      
      // Проверяем, что результат равен null
      expect(result).toBeNull();
    });
  });

  describe('createZone', () => {
    it('должен создавать новую зону', async () => {
      // Создаем тестовую зону
      const testZone: Zone = {
        name: 'new-zone',
        type: 'zone',
        environments: []
      };
      
      // Мокаем ответ от API
      const mockResponse = { ...testZone };
      
      // Устанавливаем мок для метода createZone
      (apiService.createZone as jest.Mock).mockResolvedValueOnce(mockResponse);
      
      // Вызываем функцию
      const result = await dbService.createZone(testZone);
      
      // Проверяем, что apiService.createZone был вызван с правильными параметрами
      expect(apiService.createZone).toHaveBeenCalledWith(testZone);
      
      // Проверяем результат
      expect(result).toEqual(mockResponse);
    });
  });

  describe('updateZone', () => {
    it('должен обновлять существующую зону', async () => {
      // Создаем тестовую зону
      const testZone: Zone = {
        name: 'zone1',
        type: 'zone',
        environments: [
          { name: 'prod', servers: [] }
        ]
      };
      
      // Мокаем ответ от API
      const mockResponse = { ...testZone };
      
      // Устанавливаем мок для метода updateZone
      (apiService.updateZone as jest.Mock).mockResolvedValueOnce(mockResponse);
      
      // Вызываем функцию
      const result = await dbService.updateZone(testZone);
      
      // Проверяем, что apiService.updateZone был вызван с правильными параметрами
      expect(apiService.updateZone).toHaveBeenCalledWith(testZone);
      
      // Проверяем результат
      expect(result).toEqual(mockResponse);
    });
  });

  describe('deleteZone', () => {
    it('должен удалять зону', async () => {
      // Устанавливаем мок для метода deleteZone
      (apiService.deleteZone as jest.Mock).mockResolvedValueOnce(undefined);
      
      // Вызываем функцию
      await dbService.deleteZone('zone1');
      
      // Проверяем, что apiService.deleteZone был вызван с правильными параметрами
      expect(apiService.deleteZone).toHaveBeenCalledWith('zone1');
    });
  });

  describe('addEnvironment', () => {
    it('должен добавлять окружение в зону', async () => {
      // Создаем тестовое окружение
      const testEnv = {
        name: 'dev',
        servers: []
      };
      
      // Мокаем ответ от API
      const mockResponse = {
        name: 'zone1',
        type: 'zone',
        environments: [testEnv]
      };
      
      // Устанавливаем мок для метода addEnvironment
      (apiService.addEnvironment as jest.Mock).mockResolvedValueOnce(mockResponse);
      
      // Вызываем функцию
      const result = await dbService.addEnvironment('zone1', testEnv);
      
      // Проверяем, что apiService.addEnvironment был вызван с правильными параметрами
      expect(apiService.addEnvironment).toHaveBeenCalledWith('zone1', testEnv);
      
      // Проверяем результат
      expect(result).toEqual(mockResponse);
    });
  });

  describe('addServer', () => {
    it('должен добавлять сервер в окружение', async () => {
      // Создаем тестовый сервер
      const testServer: Server = {
        fqdn: 'server1.example.com',
        ip: '192.168.1.1',
        status: 'available',
        server_type: 'web'
      };
      
      // Мокаем ответ от API
      const mockResponse = {
        name: 'zone1',
        type: 'zone',
        environments: [
          {
            name: 'prod',
            servers: [testServer]
          }
        ]
      };
      
      // Устанавливаем мок для метода addServer
      (apiService.addServer as jest.Mock).mockResolvedValueOnce(mockResponse);
      
      // Вызываем функцию
      const result = await dbService.addServer('zone1', 'prod', testServer);
      
      // Проверяем, что apiService.addServer был вызван с правильными параметрами
      expect(apiService.addServer).toHaveBeenCalledWith('zone1', 'prod', testServer);
      
      // Проверяем результат
      expect(result).toEqual(mockResponse);
    });
  });
}); 