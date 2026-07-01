import { createContext, type ReactNode, useContext, useEffect, useMemo, useState } from "react";
import { api, clearAuthToken, getAuthToken, setAuthToken } from "../lib/api";
import { LoginResponse, Perfil, User } from "../types";

type AuthContextValue = {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  hasRole: (...roles: Perfil[]) => boolean;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(Boolean(getAuthToken()));

  useEffect(() => {
    if (!getAuthToken()) return;
    api
      .get<User>("/auth/me")
      .then(setUser)
      .catch(() => {
        clearAuthToken();
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  async function login(email: string, password: string) {
    const data = await api.post<LoginResponse>("/auth/login", { email, password });
    setAuthToken(data.access_token);
    setUser(data.user);
  }

  function logout() {
    clearAuthToken();
    setUser(null);
  }

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      loading,
      login,
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
