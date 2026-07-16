import { createContext, type ReactNode, useContext, useEffect, useMemo, useState } from "react";
import { api, clearAuthToken, getAuthToken, setAuthToken } from "../lib/api";
import { LoginResponse, Perfil, User } from "../types";

type AuthContextValue = {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  demoLogin: (role: Perfil) => Promise<void>;
  activateAdmin: (token: string, password: string, passwordConfirmation: string) => Promise<void>;
  logout: () => Promise<void>;
  hasRole: (...roles: Perfil[]) => boolean;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const tokenAtStart = getAuthToken();
    api
      .get<User>("/auth/me")
      .then(setUser)
      .catch(() => {
        if (getAuthToken() === tokenAtStart) {
          clearAuthToken();
        }
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  async function login(email: string, password: string) {
    const data = await api.post<LoginResponse>("/auth/login", { email, password });
    setAuthToken(data.access_token);
    setUser(data.user);
  }

  async function demoLogin(role: Perfil) {
    const data = await api.post<LoginResponse>("/auth/demo-login", { role });
    setAuthToken(data.access_token);
    setUser(data.user);
  }

  async function activateAdmin(token: string, password: string, passwordConfirmation: string) {
    const data = await api.post<LoginResponse>("/auth/admin-bootstrap/activate", {
      token,
      password,
      password_confirmation: passwordConfirmation,
    });
    setAuthToken(data.access_token);
    setUser(data.user);
  }

  async function logout() {
    try {
      await api.post("/auth/logout", {});
    } catch {
      // A sessao local deve ser limpa mesmo se a API ja expirou o cookie.
    }
    clearAuthToken();
    setUser(null);
  }

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      loading,
      login,
      demoLogin,
      activateAdmin,
      logout,
      hasRole: (...roles) => Boolean(user && roles.includes(user.role)),
    }),
    [loading, user]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth deve ser usado dentro de AuthProvider");
  }
  return context;
}
