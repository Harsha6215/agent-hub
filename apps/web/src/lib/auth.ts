import { createContext, useContext } from "react";
import api from "./api";

export interface User {
  id: string;
  email: string;
  full_name: string | null;
  is_active: boolean;
  tier: string;
  created_at: string;
}

export interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

export const AuthContext = createContext<AuthContextType>({
  user: null,
  token: null,
  login: async () => {},
  register: async () => {},
  logout: () => {},
  isAuthenticated: false,
});

export const useAuth = () => useContext(AuthContext);

// Token management
export function getStoredToken(): string | null {
  return localStorage.getItem("access_token");
}

export function setStoredTokens(access: string, refresh: string) {
  localStorage.setItem("access_token", access);
  localStorage.setItem("refresh_token", refresh);
}

export function clearStoredTokens() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
}

export async function fetchCurrentUser(): Promise<User | null> {
  const token = getStoredToken();
  if (!token) return null;
  try {
    const res = await api.get("/api/v1/auth/me", {
      headers: { Authorization: `Bearer ${token}` },
    });
    return res.data;
  } catch {
    clearStoredTokens();
    return null;
  }
}
