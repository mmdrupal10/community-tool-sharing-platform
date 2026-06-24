import { createContext, ReactNode, useContext, useEffect, useMemo, useState } from "react";
import { apiFetch, clearToken, getToken, saveToken } from "../api/client";
import type { TokenResponse, User } from "../types";

interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (fullName: string, email: string, password: string, inviteToken: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  async function loadUser() {
    if (!getToken()) {
      setUser(null);
      setIsLoading(false);
      return;
    }
    try {
      const currentUser = await apiFetch<User>("/auth/me");
      setUser(currentUser);
    } catch {
      clearToken();
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadUser();
  }, []);

  async function login(email: string, password: string) {
    const token = await apiFetch<TokenResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password })
    });
    saveToken(token.access_token);
    await loadUser();
  }

  async function register(fullName: string, email: string, password: string, inviteToken: string) {
    const token = await apiFetch<TokenResponse>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ full_name: fullName, email, password, invite_token: inviteToken })
    });
    saveToken(token.access_token);
    await loadUser();
  }

  function logout() {
    clearToken();
    setUser(null);
  }

  const value = useMemo(
    () => ({ user, isLoading, login, register, logout }),
    [user, isLoading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return value;
}
