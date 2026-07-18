import { type FormEvent, useEffect, useRef, useState } from "react";
import { LockKeyhole } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Panel } from "../components/CrudShell";
import { PageHeader } from "../components/PageHeader";
import { api } from "../lib/api";

type ValidationResponse = {
  valid: boolean;
  expires_at?: string | null;
};

export function PasswordRecoveryReset() {
  const navigate = useNavigate();
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
    window.history.replaceState({}, document.title, "/redefinir-senha");
    setToken(tokenFromUrl);
    if (!tokenFromUrl) {
      setValid(false);
      return;
    }
    api
      .get<ValidationResponse>("/auth/password-recovery/validate", { "X-Password-Recovery-Token": tokenFromUrl })
      .then((response) => setValid(response.valid))
      .catch(() => setValid(false));
  }, []);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage("");
    setLoading(true);
    try {
      await api.post("/auth/password-recovery/confirm", {
        token: tokenRef.current || token,
        password,
        password_confirmation: passwordConfirmation,
      });
      navigate("/login", { replace: true });
    } catch {
      setMessage("Nao foi possivel redefinir a senha. Verifique o link e a senha informada.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-xl p-5">
      <PageHeader title="Redefinir senha" subtitle="Defina uma nova senha para recuperar o acesso ao CRM BBB Consig." />
      <Panel>
        {valid === null && <div className="text-sm text-slate-400">Validando link...</div>}
        {valid === false && <div className="rounded-md border border-red-500/40 bg-red-500/10 p-3 text-sm text-red-200">Link invalido ou expirado.</div>}
        {valid && (
          <form className="grid gap-3" onSubmit={submit}>
            <label className="text-sm text-slate-400">
              Nova senha
              <input className="input mt-1" type="password" value={password} onChange={(event) => setPassword(event.target.value)} />
            </label>
            <label className="text-sm text-slate-400">
              Confirmar senha
              <input className="input mt-1" type="password" value={passwordConfirmation} onChange={(event) => setPasswordConfirmation(event.target.value)} />
            </label>
            {message && <div className="rounded-md border border-red-500/40 bg-red-500/10 p-3 text-sm text-red-200">{message}</div>}
            <button className="btn" type="submit" disabled={loading}>
              <LockKeyhole size={16} /> {loading ? "Redefinindo..." : "Redefinir senha"}
            </button>
          </form>
        )}
      </Panel>
    </div>
  );
}
