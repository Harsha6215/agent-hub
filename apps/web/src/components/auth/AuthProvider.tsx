import { useEffect, useState, ReactNode } from "react";
import api from "@/lib/api";
import {
  AuthContext,
  User,
  clearStoredTokens,
  fetchCurrentUser,
  getStoredToken,
  setStoredTokens,
} from "@/lib/auth";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(getStoredToken());
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCurrentUser().then((u) => {
      setUser(u);
      setLoading(false);
    });
  }, []);

  const login = async (email: string, password: string) => {
    const res = await api.post("/api/v1/auth/login", { email, password });
    setStoredTokens(res.data.access_token, res.data.refresh_token);
    setToken(res.data.access_token);
    const u = await fetchCurrentUser();
    setUser(u);
  };

  const register = async (email: string, password: string, fullName?: string) => {
    const res = await api.post("/api/v1/auth/register", {
      email,
      password,
      full_name: fullName || null,
    });
    setStoredTokens(res.data.access_token, res.data.refresh_token);
    setToken(res.data.access_token);
    const u = await fetchCurrentUser();
    setUser(u);
  };

  const logout = () => {
    clearStoredTokens();
    setToken(null);
    setUser(null);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-900">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <AuthContext.Provider
      value={{ user, token, login, register, logout, isAuthenticated: !!user }}
    >
      {children}
    </AuthContext.Provider>
  );
}
