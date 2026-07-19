import { type FormEvent, useEffect, useRef, useState } from "react";
import { LockKeyhole } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { AuthShell } from "../components/AuthShell";
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
    <AuthShell title="Redefinir senha" subtitle="Defina uma nova senha para recuperar o acesso ao CRM BBB Consig.">
        {valid === null && <div className="text-sm font-semibold text-slate-600">Validando link...</div>}
        {valid === false && <div className="rounded-2xl border border-red-200 bg-red-50 p-3 text-sm font-semibold text-red-700">Link invalido ou expirado.</div>}
        {valid && (
          <form className="grid gap-4" onSubmit={submit}>
            <label className="text-sm font-semibold text-slate-700">
              Nova senha
              <input className="input mt-1.5" type="password" autoComplete="new-password" value={password} onChange={(event) => setPassword(event.target.value)} />
            </label>
            <label className="text-sm font-semibold text-slate-700">
              Confirmar senha
              <input className="input mt-1.5" type="password" autoComplete="new-password" value={passwordConfirmation} onChange={(event) => setPasswordConfirmation(event.target.value)} />
            </label>
            {message && <div className="rounded-2xl border border-red-200 bg-red-50 p-3 text-sm font-semibold text-red-700">{message}</div>}
            <button className="btn w-full" type="submit" disabled={loading}>
              <LockKeyhole size={16} /> {loading ? "Redefinindo..." : "Redefinir senha"}
            </button>
          </form>
        )}
    </AuthShell>
  );
}
