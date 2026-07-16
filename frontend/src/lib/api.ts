const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export function getAuthToken() {
  return null;
}

export function setAuthToken(token: string) {
  void token;
}

export function clearAuthToken() {
  localStorage.removeItem("bbb_consig_auth_token");
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const token = getAuthToken();
  const res = await fetch(`${API_URL}${path}`, {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(init?.headers ?? {}),
    },
    ...init,
  });
  if (!res.ok) {
    let detail = `Erro ${res.status} em ${path}`;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch {
      // Mantem a mensagem padrao quando a API nao retorna JSON.
    }
    if (res.status === 401) {
      clearAuthToken();
    }
    throw new Error(detail);
  }
  return res.json();
}

export const api = {
  get: <T>(path: string, headers?: Record<string, string>) => request<T>(path, { headers }),
  post: <T>(path: string, body: unknown) => request<T>(path, { method: "POST", body: JSON.stringify(body) }),
  put: <T>(path: string, body: unknown) => request<T>(path, { method: "PUT", body: JSON.stringify(body) }),
  patch: <T>(path: string, body?: unknown) => request<T>(path, { method: "PATCH", body: body ? JSON.stringify(body) : undefined }),
  delete: <T>(path: string) => request<T>(path, { method: "DELETE" }),
};

export const formatMoney = (value: number) =>
  new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(value || 0);
