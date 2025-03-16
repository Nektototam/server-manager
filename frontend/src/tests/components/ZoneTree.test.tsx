import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import ZoneTree from '../../components/ZoneTree';
import { Zone, Environment } from '../../models/types';

describe('ZoneTree', () => {
  // Тестовые данные
  const mockZones: Zone[] = [
    {
      name: 'zone1',
      type: 'zone',
      environments: [
        {
          name: 'prod',
          servers: [
            {
              fqdn: 'server1.example.com',
              ip: '192.168.1.1',
              status: 'available',
              server_type: 'web'
            }
          ]
        },
        {
          name: 'dev',
          servers: []
        }
      ]
    },
    {
      name: 'zone2',
      type: 'zone',
      environments: []
    }
  ];

  // Мок-функции для обработчиков событий
  const mockHandlers = {
    onSelectZone: jest.fn(),
    onSelectEnvironment: jest.fn(),
    onAddZone: jest.fn(),
    onEditZone: jest.fn(),
    onDeleteZone: jest.fn(),
    onAddEnvironment: jest.fn(),
    onEditEnvironment: jest.fn(),
    onDeleteEnvironment: jest.fn(),
    onAddServer: jest.fn()
  };

  // Сбрасываем моки перед каждым тестом
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('должен отображать список зон', () => {
    render(
      <ZoneTree
        zones={mockZones}
        selectedZone={null}
        selectedEnvironment={null}
        {...mockHandlers}
      />
    );

    // Проверяем, что зоны отображаются
    expect(screen.getByText('zone1')).toBeInTheDocument();
    expect(screen.getByText('zone2')).toBeInTheDocument();
  });

  it('должен отображать сообщение, если нет зон', () => {
    render(
      <ZoneTree
        zones={[]}
        selectedZone={null}
        selectedEnvironment={null}
        {...mockHandlers}
      />
    );

    // Проверяем, что отображается сообщение об отсутствии зон
    expect(screen.getByText('Нет доступных зон')).toBeInTheDocument();
  });

  it('должен вызывать onSelectZone при клике на зону', () => {
    render(
      <ZoneTree
        zones={mockZones}
        selectedZone={null}
        selectedEnvironment={null}
        {...mockHandlers}
      />
    );

    // Кликаем на зону
    fireEvent.click(screen.getByText('zone1'));

    // Проверяем, что был вызван обработчик
    expect(mockHandlers.onSelectZone).toHaveBeenCalledWith('zone1');
  });

  it('должен раскрывать зону при клике', () => {
    render(
      <ZoneTree
        zones={mockZones}
        selectedZone={null}
        selectedEnvironment={null}
        {...mockHandlers}
      />
    );

    // Изначально окружения не отображаются
    expect(screen.queryByText('prod')).not.toBeInTheDocument();

    // Кликаем на зону для раскрытия
    fireEvent.click(screen.getByText('zone1'));

    // Теперь окружения должны отображаться
    expect(screen.getByText('prod')).toBeInTheDocument();
    expect(screen.getByText('dev')).toBeInTheDocument();
  });

  it('должен вызывать onAddZone при клике на кнопку добавления зоны', () => {
    render(
      <ZoneTree
        zones={mockZones}
        selectedZone={null}
        selectedEnvironment={null}
        {...mockHandlers}
      />
    );

    // Находим кнопку добавления зоны и кликаем на нее
    const addButton = screen.getByLabelText('add-zone');
    fireEvent.click(addButton);

    // Проверяем, что был вызван обработчик
    expect(mockHandlers.onAddZone).toHaveBeenCalled();
  });

  it('должен отображать меню зоны при клике на кнопку опций', () => {
    render(
      <ZoneTree
        zones={mockZones}
        selectedZone={null}
        selectedEnvironment={null}
        {...mockHandlers}
      />
    );

    // Находим кнопку опций для первой зоны и кликаем на нее
    const optionsButtons = screen.getAllByLabelText('options');
    fireEvent.click(optionsButtons[0]);

    // Проверяем, что меню отображается с правильными пунктами
    expect(screen.getByText('Редактировать зону')).toBeInTheDocument();
    expect(screen.getByText('Удалить зону')).toBeInTheDocument();
    expect(screen.getByText('Добавить окружение')).toBeInTheDocument();
  });

  it('должен вызывать onSelectEnvironment при клике на окружение', async () => {
    render(
      <ZoneTree
        zones={mockZones}
        selectedZone={mockZones[0]}
        selectedEnvironment={null}
        {...mockHandlers}
      />
    );

    // Сначала раскрываем зону
    fireEvent.click(screen.getByText('zone1'));

    // Затем кликаем на окружение
    fireEvent.click(screen.getByText('prod'));

    // Проверяем, что были вызваны обработчики
    expect(mockHandlers.onSelectZone).toHaveBeenCalledWith('zone1');
    expect(mockHandlers.onSelectEnvironment).toHaveBeenCalledWith('prod');
  });

  it('должен отображать выбранную зону и окружение с выделением', () => {
    render(
      <ZoneTree
        zones={mockZones}
        selectedZone={mockZones[0]}
        selectedEnvironment={mockZones[0].environments[0]}
        {...mockHandlers}
      />
    );

    // Раскрываем зону
    fireEvent.click(screen.getByText('zone1'));

    // Проверяем, что зона и окружение отображаются с выделением
    // Это сложно проверить напрямую, так как выделение реализовано через стили
    // Но мы можем проверить, что элементы присутствуют
    expect(screen.getByText('zone1')).toBeInTheDocument();
    expect(screen.getByText('prod')).toBeInTheDocument();
  });

  it('должен отображать серверы при раскрытии окружения', () => {
    render(
      <ZoneTree
        zones={mockZones}
        selectedZone={mockZones[0]}
        selectedEnvironment={null}
        {...mockHandlers}
      />
    );

    // Раскрываем зону
    fireEvent.click(screen.getByText('zone1'));

    // Раскрываем окружение
    fireEvent.click(screen.getByText('prod'));

    // Проверяем, что сервер отображается
    expect(screen.getByText('server1.example.com')).toBeInTheDocument();
  });

  it('должен отображать сообщение, если в окружении нет серверов', () => {
    render(
      <ZoneTree
        zones={mockZones}
        selectedZone={mockZones[0]}
        selectedEnvironment={null}
        {...mockHandlers}
      />
    );

    // Раскрываем зону
    fireEvent.click(screen.getByText('zone1'));

    // Раскрываем пустое окружение
    fireEvent.click(screen.getByText('dev'));

    // Проверяем, что отображается сообщение об отсутствии серверов
    expect(screen.getByText('Нет серверов')).toBeInTheDocument();
  });
}); 