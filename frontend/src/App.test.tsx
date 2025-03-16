import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

// Мокаем react-router-dom
jest.mock('react-router-dom', () => ({
  BrowserRouter: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Routes: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Route: () => <div>Route</div>,
  Navigate: () => <div>Navigate</div>,
}));

// Мокаем контексты
jest.mock('./context/AuthContext', () => ({
  AuthProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  useAuth: () => ({
    isAuthenticated: false,
    loading: false,
  }),
}));

jest.mock('./context/DataContext', () => ({
  DataProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

// Мокаем страницы
jest.mock('./pages/LoginPage', () => () => <div>Login Page</div>);
jest.mock('./pages/MainPage', () => () => <div>Main Page</div>);

test('рендерит приложение без ошибок', () => {
  render(<App />);
  
  // Проверяем, что компонент рендерится без ошибок
  // Так как мы мокаем все компоненты, мы просто проверяем, что приложение рендерится
  expect(document.body).toBeInTheDocument();
});
