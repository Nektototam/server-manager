// Типы для серверных данных
export interface Server {
  fqdn: string;
  ip: string;
  status: 'available' | 'unavailable';
  server_type: string;
}

export interface Environment {
  name: string;
  servers: Server[];
}

export interface Zone {
  _id?: string;
  _rev?: string;
  name: string;
  type: string;
  environments: Environment[];
}

// Типы для аутентификации
export interface User {
  username: string;
  email?: string;
  full_name?: string;
  disabled?: boolean;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

// Типы для управления состоянием
export interface AppState {
  isAuthenticated: boolean;
  token: string | null;
  user: User | null;
  zones: Zone[];
  selectedZone: Zone | null;
  selectedEnvironment: Environment | null;
  loading: boolean;
  error: string | null;
}

// Типы для запросов API
export interface LoginRequest {
  username: string;
  password: string;
} 