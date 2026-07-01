import { useCallback, useEffect, useState, type DependencyList } from "react";

export function useAsync<T>(loader: () => Promise<T>, deps: DependencyList = []) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const reload = useCallback(() => {
    setLoading(true);
    setError(null);
    loader()
      .then(setData)
      .catch((err) => setError(err.message ?? "Erro ao carregar"))
      .finally(() => setLoading(false));
  }, deps);

  useEffect(() => reload(), [reload]);
  return { data, loading, error, reload };
}
