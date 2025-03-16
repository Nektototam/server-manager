import { dbService } from '../../services/dbService';
import { Zone, Server } from '../../models/types';

// Мокаем PouchDB
jest.mock('pouchdb-browser', () => {
  return function() {
    return {
      get: jest.fn(),
      put: jest.fn(),
      post: jest.fn(),
      remove: jest.fn(),
      allDocs: jest.fn(),
      changes: jest.fn(() => ({
        on: jest.fn(),
        cancel: jest.fn()
      })),
      sync: jest.fn(() => ({
        on: jest.fn(),
        cancel: jest.fn()
      }))
    };
  };
});

describe('dbService', () => {
  // Сбрасываем моки перед каждым тестом
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('getZones', () => {
    it('должен возвращать список зон из базы данных', async () => {
      // Мокаем ответ от PouchDB
      const mockZones = {
        rows: [
          {
            doc: {
              _id: 'zone1',
              _rev: '1-abc',
              name: 'zone1',
              type: 'zone',
              environments: []
            }
          },
          {
            doc: {
              _id: 'zone2',
              _rev: '1-def',
              name: 'zone2',
              type: 'zone',
              environments: []
            }
          }
        ]
      };
      
      // Устанавливаем мок для метода allDocs
      (dbService as any).db.allDocs.mockResolvedValueOnce(mockZones);
      
      // Вызываем функцию
      const result = await dbService.getZones();
      
      // Проверяем, что allDocs был вызван с правильными параметрами
      expect((dbService as any).db.allDocs).toHaveBeenCalledWith({
        include_docs: true
      });
      
      // Проверяем результат
      expect(result).toEqual([
        {
          _id: 'zone1',
          _rev: '1-abc',
          name: 'zone1',
          type: 'zone',
          environments: []
        },
        {
          _id: 'zone2',
          _rev: '1-def',
          name: 'zone2',
          type: 'zone',
          environments: []
        }
      ]);
    });
  });

  describe('getZone', () => {
    it('должен возвращать зону по имени', async () => {
      // Мокаем ответ от PouchDB
      const mockZone = {
        _id: 'zone1',
        _rev: '1-abc',
        name: 'zone1',
        type: 'zone',
        environments: [
          { name: 'prod', servers: [] }
        ]
      };
      
      // Устанавливаем мок для метода get
      (dbService as any).db.get.mockResolvedValueOnce(mockZone);
      
      // Вызываем функцию
      const result = await dbService.getZone('zone1');
      
      // Проверяем, что get был вызван с правильными параметрами
      expect((dbService as any).db.get).toHaveBeenCalledWith('zone1');
      
      // Проверяем результат
      expect(result).toEqual(mockZone);
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
      
      // Мокаем ответ от PouchDB
      const mockResponse = {
        id: 'new-zone',
        rev: '1-abc',
        ok: true
      };
      
      // Устанавливаем мок для метода post
      (dbService as any).db.post.mockResolvedValueOnce(mockResponse);
      
      // Вызываем функцию
      const result = await dbService.createZone(testZone);
      
      // Проверяем, что post был вызван с правильными параметрами
      expect((dbService as any).db.post).toHaveBeenCalledWith(testZone);
      
      // Проверяем результат
      expect(result).toEqual({
        ...testZone,
        _id: 'new-zone',
        _rev: '1-abc'
      });
    });
  });

  describe('updateZone', () => {
    it('должен обновлять существующую зону', async () => {
      // Создаем тестовую зону
      const testZone: Zone = {
        _id: 'zone1',
        _rev: '1-abc',
        name: 'zone1',
        type: 'zone',
        environments: [
          { name: 'prod', servers: [] }
        ]
      };
      
      // Мокаем ответ от PouchDB
      const mockResponse = {
        id: 'zone1',
        rev: '2-def',
        ok: true
      };
      
      // Устанавливаем мок для метода put
      (dbService as any).db.put.mockResolvedValueOnce(mockResponse);
      
      // Вызываем функцию
      const result = await dbService.updateZone(testZone);
      
      // Проверяем, что put был вызван с правильными параметрами
      expect((dbService as any).db.put).toHaveBeenCalledWith(testZone);
      
      // Проверяем результат
      expect(result).toEqual({
        ...testZone,
        _rev: '2-def'
      });
    });
  });

  describe('deleteZone', () => {
    it('должен удалять зону', async () => {
      // Мокаем ответ от PouchDB для get
      const mockZone = {
        _id: 'zone1',
        _rev: '1-abc',
        name: 'zone1',
        type: 'zone',
        environments: []
      };
      
      // Мокаем ответ от PouchDB для remove
      const mockResponse = {
        id: 'zone1',
        rev: '2-def',
        ok: true
      };
      
      // Устанавливаем моки для методов
      (dbService as any).db.get.mockResolvedValueOnce(mockZone);
      (dbService as any).db.remove.mockResolvedValueOnce(mockResponse);
      
      // Вызываем функцию
      await dbService.deleteZone('zone1');
      
      // Проверяем, что get был вызван с правильными параметрами
      expect((dbService as any).db.get).toHaveBeenCalledWith('zone1');
      
      // Проверяем, что remove был вызван с правильными параметрами
      expect((dbService as any).db.remove).toHaveBeenCalledWith(mockZone);
    });
  });

  describe('addEnvironment', () => {
    it('должен добавлять окружение в зону', async () => {
      // Мокаем ответ от PouchDB для get
      const mockZone = {
        _id: 'zone1',
        _rev: '1-abc',
        name: 'zone1',
        type: 'zone',
        environments: []
      };
      
      // Мокаем ответ от PouchDB для put
      const mockResponse = {
        id: 'zone1',
        rev: '2-def',
        ok: true
      };
      
      // Устанавливаем моки для методов
      (dbService as any).db.get.mockResolvedValueOnce(mockZone);
      (dbService as any).db.put.mockResolvedValueOnce(mockResponse);
      
      // Вызываем функцию
      const result = await dbService.addEnvironment('zone1', { name: 'dev', servers: [] });
      
      // Проверяем, что get был вызван с правильными параметрами
      expect((dbService as any).db.get).toHaveBeenCalledWith('zone1');
      
      // Проверяем, что put был вызван с правильными параметрами
      expect((dbService as any).db.put).toHaveBeenCalledWith({
        ...mockZone,
        environments: [{ name: 'dev', servers: [] }]
      });
      
      // Проверяем результат
      expect(result).toEqual({
        ...mockZone,
        _rev: '2-def',
        environments: [{ name: 'dev', servers: [] }]
      });
    });
  });

  describe('addServer', () => {
    it('должен добавлять сервер в окружение', async () => {
      // Мокаем ответ от PouchDB для get
      const mockZone = {
        _id: 'zone1',
        _rev: '1-abc',
        name: 'zone1',
        type: 'zone',
        environments: [
          { name: 'prod', servers: [] }
        ]
      };
      
      // Мокаем ответ от PouchDB для put
      const mockResponse = {
        id: 'zone1',
        rev: '2-def',
        ok: true
      };
      
      // Создаем тестовый сервер
      const testServer: Server = {
        fqdn: 'server1.example.com',
        ip: '192.168.1.1',
        status: 'available',
        server_type: 'web'
      };
      
      // Устанавливаем моки для методов
      (dbService as any).db.get.mockResolvedValueOnce(mockZone);
      (dbService as any).db.put.mockResolvedValueOnce(mockResponse);
      
      // Вызываем функцию
      const result = await dbService.addServer('zone1', 'prod', testServer);
      
      // Проверяем, что get был вызван с правильными параметрами
      expect((dbService as any).db.get).toHaveBeenCalledWith('zone1');
      
      // Проверяем, что put был вызван с правильными параметрами
      expect((dbService as any).db.put).toHaveBeenCalledWith({
        ...mockZone,
        environments: [
          { name: 'prod', servers: [testServer] }
        ]
      });
      
      // Проверяем результат
      expect(result).toEqual({
        ...mockZone,
        _rev: '2-def',
        environments: [
          { name: 'prod', servers: [testServer] }
        ]
      });
    });
  });
}); 