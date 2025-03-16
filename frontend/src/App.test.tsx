import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

// Мокаем react-router-dom
jest.mock('react-router-dom', () => ({
  BrowserRouter: ({ children }: { children: React.ReactNode }) => <div data-testid="browser-router">{children}</div>,
  Routes: ({ children }: { children: React.ReactNode }) => <div data-testid="routes">{children}</div>,
  Route: () => <div data-testid="route">Route</div>,
  Navigate: () => <div data-testid="navigate">Navigate</div>,
}));

// Мокаем контексты
jest.mock('./context/AuthContext', () => ({
  AuthProvider: ({ children }: { children: React.ReactNode }) => <div data-testid="auth-provider">{children}</div>,
  useAuth: () => ({
    isAuthenticated: false,
    loading: false,
  }),
}));

jest.mock('./context/DataContext', () => ({
  DataProvider: ({ children }: { children: React.ReactNode }) => <div data-testid="data-provider">{children}</div>,
}));

// Мокаем страницы
jest.mock('./pages/LoginPage', () => () => <div data-testid="login-page">Login Page</div>);
jest.mock('./pages/MainPage', () => () => <div data-testid="main-page">Main Page</div>);

test('рендерит приложение без ошибок', () => {
  render(<App />);
  
  // Проверяем, что компонент рендерится без ошибок
  expect(screen.getByTestId('browser-router')).toBeInTheDocument();
  expect(screen.getByTestId('auth-provider')).toBeInTheDocument();
  expect(screen.getByTestId('data-provider')).toBeInTheDocument();
});
