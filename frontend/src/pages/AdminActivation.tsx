import { type FormEvent, useEffect, useRef, useState } from "react";
import { LockKeyhole } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { api } from "../lib/api";
import { useAuth } from "../auth/AuthContext";
import { Panel } from "../components/CrudShell";
import { PageHeader } from "../components/PageHeader";

type ValidationResponse = {
  valid: boolean;
  expires_at?: string | null;
};

export function AdminActivation() {
  const navigate = useNavigate();
  const { activateAdmin } = useAuth();
  const [token, setToken] = useState("");
  const tokenRef = useRef("");
  const tokenLoadedRef = useRef(false);
  const [valid, setValid] = useState<boolean | null>(null);
  const [password, setPassword] = useState("");
  const [passwordConfirmation, setPasswordConfirmation] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (tokenLoadedRef.current) {
      return;
    }
    tokenLoadedRef.current = true;
    const params = new URLSearchParams(window.location.search);
    const tokenFromUrl = params.get("token") ?? "";
    tokenRef.current = tokenFromUrl;
    window.history.replaceState({}, document.title, "/ativar-admin");
    setToken(tokenFromUrl);
    if (!tokenFromUrl) {
      setValid(false);
      return;
    }
    api
      .get<ValidationResponse>("/auth/admin-bootstrap/validate", { "X-Admin-Bootstrap-Token": tokenFromUrl })
      .then((response) => setValid(response.valid))
      .catch(() => setValid(false));
  }, []);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage("");
    setLoading(true);
    try {
      await activateAdmin(tokenRef.current || token, password, passwordConfirmation);
      navigate("/dashboard", { replace: true });
    } catch {
      setMessage("Nao foi possivel ativar este acesso. Verifique o link e a senha informada.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-xl p-5">
      <PageHeader title="Ativar administrador" subtitle="Defina sua senha para acessar o CRM BBB Consig." />
      <Panel>
        {valid === null && <div className="text-sm text-slate-500">Validando link...</div>}
        {valid === false && <div className="alert-error">Link invalido ou expirado.</div>}
        {valid && (
          <form className="grid gap-3" onSubmit={submit}>
            <label className="text-sm text-slate-500">
              Nova senha
              <input className="input mt-1" type="password" value={password} onChange={(event) => setPassword(event.target.value)} />
            </label>
            <label className="text-sm text-slate-500">
              Confirmar senha
              <input className="input mt-1" type="password" value={passwordConfirmation} onChange={(event) => setPasswordConfirmation(event.target.value)} />
            </label>
            {message && <div className="alert-error">{message}</div>}
            <button className="btn" type="submit" disabled={loading}>
              <LockKeyhole size={16} /> {loading ? "Ativando..." : "Ativar acesso"}
            </button>
          </form>
        )}
      </Panel>
    </div>
  );
}
