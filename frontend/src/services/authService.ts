import { User, AuthResponse, LoginPayload, SignupPayload } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8020';

// In-memory access token storage (never stored in localStorage to prevent XSS exfiltration)
let inMemoryAccessToken: string | null = null;

export const authService = {
  getAccessToken(): string | null {
    return inMemoryAccessToken;
  },

  setAccessToken(token: string | null): void {
    inMemoryAccessToken = token;
  },

  async login(credentials: LoginPayload): Promise<AuthResponse> {
    const res = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include', // Includes HttpOnly refresh token cookie
      body: JSON.stringify(credentials),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Authentication failed' }));
      throw new Error(err.detail || `Login error HTTP ${res.status}`);
    }

    const data: AuthResponse = await res.json();
    this.setAccessToken(data.accessToken);
    return data;
  },

  async signup(payload: SignupPayload): Promise<AuthResponse> {
    const res = await fetch(`${API_BASE_URL}/api/auth/signup`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({
        full_name: payload.fullName,
        email: payload.email,
        password: payload.password,
      }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Signup failed' }));
      throw new Error(err.detail || `Registration error HTTP ${res.status}`);
    }

    const data: AuthResponse = await res.json();
    this.setAccessToken(data.accessToken);
    return data;
  },

  async refreshToken(): Promise<string | null> {
    try {
      const res = await fetch(`${API_BASE_URL}/api/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Sends HttpOnly cookie
      });

      if (!res.ok) {
        this.setAccessToken(null);
        return null;
      }

      const data: AuthResponse = await res.json();
      this.setAccessToken(data.accessToken);
      return data.accessToken;
    } catch {
      this.setAccessToken(null);
      return null;
    }
  },

  async getMe(): Promise<User | null> {
    const token = this.getAccessToken();
    if (!token) return null;

    try {
      const res = await fetch(`${API_BASE_URL}/api/auth/me`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!res.ok) return null;
      return await res.json();
    } catch {
      return null;
    }
  },

  async logout(): Promise<void> {
    try {
      await fetch(`${API_BASE_URL}/api/auth/logout`, {
        method: 'POST',
        credentials: 'include',
      });
    } catch (e) {
      console.warn('Logout request warning:', e);
    } finally {
      this.setAccessToken(null);
    }
  },
};

