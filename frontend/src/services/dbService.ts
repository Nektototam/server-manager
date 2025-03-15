import { Zone, Server, Environment } from '../models/types';
import { apiService } from './apiService';

class DbService {
  // Получить все зоны
  public async getZones(): Promise<Zone[]> {
    try {
      const response = await apiService.getZones();
      return response;
    } catch (error) {
      console.error('Ошибка при получении зон:', error);
      throw error;
    }
  }

  // Получить зону по имени
  public async getZone(zoneName: string): Promise<Zone | null> {
    try {
      const response = await apiService.getZone(zoneName);
      return response;
    } catch (error) {
      console.error('Ошибка при получении зоны:', error);
      return null;
    }
  }

  // Создать зону
  public async createZone(zone: Zone): Promise<Zone> {
    try {
      const response = await apiService.createZone(zone);
      return response;
    } catch (error) {
      console.error('Ошибка при создании зоны:', error);
      throw error;
    }
  }

  // Обновить зону
  public async updateZone(zone: Zone): Promise<Zone> {
    try {
      const response = await apiService.updateZone(zone);
      return response;
    } catch (error) {
      console.error('Ошибка при обновлении зоны:', error);
      throw error;
    }
  }

  // Удалить зону
  public async deleteZone(zoneName: string): Promise<void> {
    try {
      await apiService.deleteZone(zoneName);
    } catch (error) {
      console.error('Ошибка при удалении зоны:', error);
      throw error;
    }
  }

  // Методы для работы с окружениями
  public async addEnvironment(zoneName: string, environment: Environment): Promise<Zone> {
    try {
      const response = await apiService.addEnvironment(zoneName, environment);
      return response;
    } catch (error) {
      console.error('Ошибка при добавлении окружения:', error);
      throw error;
    }
  }

  public async updateEnvironment(zoneName: string, envName: string, environment: Environment): Promise<Zone> {
    try {
      const response = await apiService.updateEnvironment(zoneName, envName, environment);
      return response;
    } catch (error) {
      console.error('Ошибка при обновлении окружения:', error);
      throw error;
    }
  }

  public async deleteEnvironment(zoneName: string, envName: string): Promise<Zone> {
    try {
      const response = await apiService.deleteEnvironment(zoneName, envName);
      return response;
    } catch (error) {
      console.error('Ошибка при удалении окружения:', error);
      throw error;
    }
  }

  // Методы для работы с серверами
  public async addServer(zoneName: string, envName: string, server: Server): Promise<Zone> {
    try {
      const response = await apiService.addServer(zoneName, envName, server);
      return response;
    } catch (error) {
      console.error('Ошибка при добавлении сервера:', error);
      throw error;
    }
  }

  public async updateServer(zoneName: string, envName: string, serverFqdn: string, server: Server): Promise<Zone> {
    try {
      const response = await apiService.updateServer(zoneName, envName, serverFqdn, server);
      return response;
    } catch (error) {
      console.error('Ошибка при обновлении сервера:', error);
      throw error;
    }
  }

  public async deleteServer(zoneName: string, envName: string, serverFqdn: string): Promise<Zone> {
    try {
      const response = await apiService.deleteServer(zoneName, envName, serverFqdn);
      return response;
    } catch (error) {
      console.error('Ошибка при удалении сервера:', error);
      throw error;
    }
  }
}

export const dbService = new DbService(); 