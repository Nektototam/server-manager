import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { Zone, Environment, Server } from '../models/types';
import { dbService } from '../services/dbService';
import { useAuth } from './AuthContext';

// Интерфейс контекста данных
interface DataContextType {
  zones: Zone[];
  selectedZone: Zone | null;
  selectedEnvironment: Environment | null;
  loading: boolean;
  error: string | null;
  fetchZones: () => Promise<void>;
  selectZone: (zoneName: string) => Promise<void>;
  selectEnvironment: (envName: string) => void;
  createZone: (zone: Zone) => Promise<Zone>;
  updateZone: (zone: Zone) => Promise<Zone>;
  deleteZone: (zoneName: string) => Promise<void>;
  createEnvironment: (zoneName: string, environment: Environment) => Promise<Zone>;
  updateEnvironment: (zoneName: string, envName: string, environment: Environment) => Promise<Zone>;
  deleteEnvironment: (zoneName: string, envName: string) => Promise<Zone>;
  addServer: (zoneName: string, envName: string, server: Server) => Promise<Zone>;
  updateServer: (zoneName: string, envName: string, serverFqdn: string, server: Server) => Promise<Zone>;
  deleteServer: (zoneName: string, envName: string, serverFqdn: string) => Promise<Zone>;
}

// Создание контекста с дефолтными значениями
const DataContext = createContext<DataContextType>({
  zones: [],
  selectedZone: null,
  selectedEnvironment: null,
  loading: false,
  error: null,
  fetchZones: async () => {},
  selectZone: async () => {},
  selectEnvironment: () => {},
  createZone: async () => ({ name: '', type: 'zone', environments: [] }),
  updateZone: async () => ({ name: '', type: 'zone', environments: [] }),
  deleteZone: async () => {},
  createEnvironment: async () => ({ name: '', type: 'zone', environments: [] }),
  updateEnvironment: async () => ({ name: '', type: 'zone', environments: [] }),
  deleteEnvironment: async () => ({ name: '', type: 'zone', environments: [] }),
  addServer: async () => ({ name: '', type: 'zone', environments: [] }),
  updateServer: async () => ({ name: '', type: 'zone', environments: [] }),
  deleteServer: async () => ({ name: '', type: 'zone', environments: [] }),
});

// Хук для использования контекста
export const useData = () => useContext(DataContext);

// Провайдер контекста
export const DataProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  const [zones, setZones] = useState<Zone[]>([]);
  const [selectedZone, setSelectedZone] = useState<Zone | null>(null);
  const [selectedEnvironment, setSelectedEnvironment] = useState<Environment | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Загрузка зон при авторизации
  useEffect(() => {
    if (isAuthenticated) {
      fetchZones();
    }
  }, [isAuthenticated]);

  // Получение всех зон
  const fetchZones = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const zonesData = await dbService.getZones();
      setZones(zonesData);
      
      // Сбрасываем выбранную зону и окружение
      setSelectedZone(null);
      setSelectedEnvironment(null);
    } catch (error) {
      console.error('Ошибка при загрузке зон:', error);
      setError('Не удалось загрузить зоны');
    } finally {
      setLoading(false);
    }
  };

  // Выбор зоны
  const selectZone = async (zoneName: string) => {
    try {
      setLoading(true);
      
      const zone = await dbService.getZone(zoneName);
      
      if (zone) {
        setSelectedZone(zone);
        setSelectedEnvironment(null);
      } else {
        setError(`Зона ${zoneName} не найдена`);
      }
    } catch (error) {
      console.error(`Ошибка при выборе зоны ${zoneName}:`, error);
      setError(`Не удалось загрузить зону ${zoneName}`);
    } finally {
      setLoading(false);
    }
  };

  // Выбор окружения
  const selectEnvironment = (envName: string) => {
    if (!selectedZone) {
      setError('Сначала выберите зону');
      return;
    }
    
    const environment = selectedZone.environments.find(env => env.name === envName);
    
    if (environment) {
      setSelectedEnvironment(environment);
    } else {
      setError(`Окружение ${envName} не найдено в зоне ${selectedZone.name}`);
    }
  };

  // Создание зоны
  const createZone = async (zone: Zone): Promise<Zone> => {
    try {
      setLoading(true);
      
      const newZone = await dbService.createZone(zone);
      
      // Обновляем список зон
      await fetchZones();
      
      return newZone;
    } catch (error) {
      console.error('Ошибка при создании зоны:', error);
      setError('Не удалось создать зону');
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // Обновление зоны
  const updateZone = async (zone: Zone): Promise<Zone> => {
    try {
      setLoading(true);
      
      const updatedZone = await dbService.updateZone(zone);
      
      // Обновляем список зон
      await fetchZones();
      
      // Если выбрана эта зона, обновляем ее
      if (selectedZone && selectedZone.name === zone.name) {
        setSelectedZone(updatedZone);
      }
      
      return updatedZone;
    } catch (error) {
      console.error('Ошибка при обновлении зоны:', error);
      setError('Не удалось обновить зону');
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // Удаление зоны
  const deleteZone = async (zoneName: string): Promise<void> => {
    try {
      setLoading(true);
      
      await dbService.deleteZone(zoneName);
      
      // Обновляем список зон
      await fetchZones();
      
      // Если выбрана эта зона, сбрасываем выбор
      if (selectedZone && selectedZone.name === zoneName) {
        setSelectedZone(null);
        setSelectedEnvironment(null);
      }
    } catch (error) {
      console.error('Ошибка при удалении зоны:', error);
      setError('Не удалось удалить зону');
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // Создание окружения
  const createEnvironment = async (zoneName: string, environment: Environment): Promise<Zone> => {
    try {
      setLoading(true);
      
      const updatedZone = await dbService.addEnvironment(zoneName, environment);
      
      // Обновляем список зон
      await fetchZones();
      
      // Если выбрана эта зона, обновляем ее
      if (selectedZone && selectedZone.name === zoneName) {
        setSelectedZone(updatedZone);
      }
      
      return updatedZone;
    } catch (error) {
      console.error('Ошибка при создании окружения:', error);
      setError('Не удалось создать окружение');
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // Обновление окружения
  const updateEnvironment = async (zoneName: string, envName: string, environment: Environment): Promise<Zone> => {
    try {
      setLoading(true);
      
      const updatedZone = await dbService.updateEnvironment(zoneName, envName, environment);
      
      // Обновляем список зон
      await fetchZones();
      
      // Если выбрана эта зона, обновляем ее
      if (selectedZone && selectedZone.name === zoneName) {
        setSelectedZone(updatedZone);
        
        // Если выбрано это окружение, обновляем его
        if (selectedEnvironment && selectedEnvironment.name === envName) {
          const updatedEnv = updatedZone.environments.find(env => env.name === environment.name);
          if (updatedEnv) {
            setSelectedEnvironment(updatedEnv);
          }
        }
      }
      
      return updatedZone;
    } catch (error) {
      console.error('Ошибка при обновлении окружения:', error);
      setError('Не удалось обновить окружение');
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // Удаление окружения
  const deleteEnvironment = async (zoneName: string, envName: string): Promise<Zone> => {
    try {
      setLoading(true);
      
      const updatedZone = await dbService.deleteEnvironment(zoneName, envName);
      
      // Обновляем список зон
      await fetchZones();
      
      // Если выбрана эта зона, обновляем ее
      if (selectedZone && selectedZone.name === zoneName) {
        setSelectedZone(updatedZone);
        
        // Если выбрано это окружение, сбрасываем выбор
        if (selectedEnvironment && selectedEnvironment.name === envName) {
          setSelectedEnvironment(null);
        }
      }
      
      return updatedZone;
    } catch (error) {
      console.error('Ошибка при удалении окружения:', error);
      setError('Не удалось удалить окружение');
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // Добавление сервера
  const addServer = async (zoneName: string, envName: string, server: Server): Promise<Zone> => {
    try {
      setLoading(true);
      
      const updatedZone = await dbService.addServer(zoneName, envName, server);
      
      // Обновляем список зон
      await fetchZones();
      
      // Если выбрана эта зона, обновляем ее
      if (selectedZone && selectedZone.name === zoneName) {
        setSelectedZone(updatedZone);
        
        // Если выбрано это окружение, обновляем его
        if (selectedEnvironment && selectedEnvironment.name === envName) {
          const updatedEnv = updatedZone.environments.find(env => env.name === envName);
          if (updatedEnv) {
            setSelectedEnvironment(updatedEnv);
          }
        }
      }
      
      return updatedZone;
    } catch (error) {
      console.error('Ошибка при добавлении сервера:', error);
      setError('Не удалось добавить сервер');
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // Обновление сервера
  const updateServer = async (zoneName: string, envName: string, serverFqdn: string, server: Server): Promise<Zone> => {
    try {
      setLoading(true);
      
      const updatedZone = await dbService.updateServer(zoneName, envName, serverFqdn, server);
      
      // Обновляем список зон
      await fetchZones();
      
      // Если выбрана эта зона, обновляем ее
      if (selectedZone && selectedZone.name === zoneName) {
        setSelectedZone(updatedZone);
        
        // Если выбрано это окружение, обновляем его
        if (selectedEnvironment && selectedEnvironment.name === envName) {
          const updatedEnv = updatedZone.environments.find(env => env.name === envName);
          if (updatedEnv) {
            setSelectedEnvironment(updatedEnv);
          }
        }
      }
      
      return updatedZone;
    } catch (error) {
      console.error('Ошибка при обновлении сервера:', error);
      setError('Не удалось обновить сервер');
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // Удаление сервера
  const deleteServer = async (zoneName: string, envName: string, serverFqdn: string): Promise<Zone> => {
    try {
      setLoading(true);
      
      const updatedZone = await dbService.deleteServer(zoneName, envName, serverFqdn);
      
      // Обновляем список зон
      await fetchZones();
      
      // Если выбрана эта зона, обновляем ее
      if (selectedZone && selectedZone.name === zoneName) {
        setSelectedZone(updatedZone);
        
        // Если выбрано это окружение, обновляем его
        if (selectedEnvironment && selectedEnvironment.name === envName) {
          const updatedEnv = updatedZone.environments.find(env => env.name === envName);
          if (updatedEnv) {
            setSelectedEnvironment(updatedEnv);
          }
        }
      }
      
      return updatedZone;
    } catch (error) {
      console.error('Ошибка при удалении сервера:', error);
      setError('Не удалось удалить сервер');
      throw error;
    } finally {
      setLoading(false);
    }
  };

  return (
    <DataContext.Provider
      value={{
        zones,
        selectedZone,
        selectedEnvironment,
        loading,
        error,
        fetchZones,
        selectZone,
        selectEnvironment,
        createZone,
        updateZone,
        deleteZone,
        createEnvironment,
        updateEnvironment,
        deleteEnvironment,
        addServer,
        updateServer,
        deleteServer,
      }}
    >
      {children}
    </DataContext.Provider>
  );
}; 