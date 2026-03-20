const API_BASE_URL = 'http://localhost:5000';

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface AuthResponse {
  token: string;
  user: {
    id: string;
    email: string;
    name?: string;
  };
}

export class AuthService {
  static async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await fetch(`${API_BASE_URL}/api/v1/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(credentials),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    const data = await response.json();
    
    // Store token in localStorage
    localStorage.setItem('auth_token', data.token);
    localStorage.setItem('user', JSON.stringify(data.user));
    
    return data;
  }

  static logout(): void {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
  }

  static getToken(): string | null {
    return localStorage.getItem('auth_token');
  }

  static getUser(): any {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  }

  static isAuthenticated(): boolean {
    return !!this.getToken();
  }
}
