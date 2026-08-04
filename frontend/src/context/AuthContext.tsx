import { createContext, useContext, useState, type ReactNode } from "react";
import { api } from "../api/client";

interface AuthState {
  isAuthenticated: boolean;
  shopName: string | null;
  currency: string | null;
  login: (email: string, password: string) => Promise<void>;
  signup: (shopName: string, email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [shopName, setShopName] = useState<string | null>(localStorage.getItem("shop_name"));
  const [currency, setCurrency] = useState<string | null>(localStorage.getItem("currency"));
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(!!localStorage.getItem("token"));

  function saveSession(data: { access_token: string; shop_name: string; currency: string }) {
    localStorage.setItem("token", data.access_token);
    localStorage.setItem("shop_name", data.shop_name);
    localStorage.setItem("currency", data.currency);
    setShopName(data.shop_name);
    setCurrency(data.currency);
    setIsAuthenticated(true);
  }

  async function login(email: string, password: string) {
    const res = await api.post("/auth/login", { email, password });
    saveSession(res.data);
  }

  async function signup(shop_name: string, email: string, password: string) {
    const res = await api.post("/auth/signup", { shop_name, email, password });
    saveSession(res.data);
  }

  function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("shop_name");
    localStorage.removeItem("currency");
    setIsAuthenticated(false);
    setShopName(null);
    setCurrency(null);
  }

  return (
    <AuthContext.Provider value={{ isAuthenticated, shopName, currency, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}
